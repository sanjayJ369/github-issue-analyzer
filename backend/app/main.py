from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import asyncio
import logging
import os
from typing import List

# App modules
from .schemas import AnalyzeRequest, AnalyzeResponse, AnalyzeResponseMeta, LLMProviderResponse
from .github_client import GitHubClient
from .llm.router import analyze_with_provider, ProviderSelectionError, LLMRateLimitError
from .llm.providers import get_provider_info_list, get_available_providers, discover_providers
from .utils import parse_github_url, build_issue_context, truncate_text
from .config import Config

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine root path for Vercel deployment
root_path = "/api" if os.getenv("VERCEL") else ""

app = FastAPI(title="GitHub Issue Analyzer API", version="1.0.0", root_path=root_path)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
gh_client = GitHubClient(token=Config.GITHUB_TOKEN)

# Caching: Key = (repo_url, issue_number, provider_id), Value = AnalyzeResponse
# TTL = 15 minutes (900 seconds)
analysis_cache = TTLCache(maxsize=100, ttl=900)


@app.get("/llm/providers", response_model=List[LLMProviderResponse])
async def list_providers(refresh: bool = False):
    """
    List all available LLM providers.
    Performs async discovery of models with latency measurement.
    
    Query params:
        refresh: Force refresh provider discovery (bypass cache)
    
    Returns list of configured providers with their IDs, models, status, and latency.
    """
    # Trigger async discovery
    providers = await discover_providers(force_refresh=refresh)
    
    # Log discovery results for debugging
    available_count = sum(1 for p in providers if p.status.value == 'available')
    logger.info(f"Provider discovery: {available_count} available, {len(providers)} total")
    
    return [
        LLMProviderResponse(
            id=p.id,
            label=p.label,
            provider=p.provider,
            model=p.model,
            is_available=p.is_available,
            status=p.status.value,  # Convert enum to string
            latency_ms=p.latency_ms,
            speed=p.speed,
            error_message=p.error_message
        )
        for p in providers
    ]


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_issue(request: AnalyzeRequest):
    """
    Analyze a GitHub issue using the selected LLM provider.
    
    If provider_id is not specified:
    - Auto-selects if exactly 1 provider is available
    - Returns error if multiple providers require selection
    """
    # Determine effective provider_id for caching
    providers = get_available_providers()
    effective_provider_id = request.provider_id
    
    if not effective_provider_id and len(providers) == 1:
        effective_provider_id = providers[0].id
    
    # 0. Check Cache (including provider_id in key)
    cache_key = (request.repo_url, request.issue_number, effective_provider_id)
    if cache_key in analysis_cache:
        logger.info(f"Serving cached result for {cache_key}")
        cached_resp = analysis_cache[cache_key].model_copy(deep=True)
        cached_resp.meta.cached = True
        return cached_resp

    # 1. Parse URL
    owner, repo = parse_github_url(request.repo_url)
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    try:
        # 2. Fetch Data (Parallel fetch for speed)
        issue_task = gh_client.fetch_issue(owner, repo, request.issue_number)
        comments_task = gh_client.fetch_comments(owner, repo, request.issue_number)
        labels_task = gh_client.fetch_labels(owner, repo)
        
        issue_data, comments_data, repo_labels = await asyncio.gather(
            issue_task, comments_task, labels_task, return_exceptions=True
        )
        
        # Check for critical errors (issue_data is required)
        if isinstance(issue_data, Exception):
            raise issue_data
        
        # Comments and labels can fail gracefully
        if isinstance(comments_data, Exception):
            logger.warning(f"Failed to fetch comments: {comments_data}")
            comments_data = []
            
        if isinstance(repo_labels, Exception):
            logger.warning(f"Failed to fetch labels: {repo_labels}")
            repo_labels = []

        # 3. Build Context
        full_text = build_issue_context(issue_data, comments_data)
        truncated_text, is_truncated = truncate_text(full_text)
        
        # 4. Analyze with LLM (using router)
        analysis = await analyze_with_provider(
            provider_id=request.provider_id,
            context=truncated_text,
            allowed_labels=repo_labels
        )
        
        # Check for warnings (e.g. closed issue)
        warning_msg = None
        if issue_data.get("state") == "closed":
            warning_msg = "This issue is currently closed. Analyzed data may be outdated."

        # 5. Construct Response
        response = AnalyzeResponse(
            analysis=analysis,
            meta=AnalyzeResponseMeta(
                issue_url=request.repo_url,
                fetched_comments_count=len(comments_data),
                truncated=is_truncated,
                cached=False,
                warning=warning_msg,
                provider_id=effective_provider_id
            )
        )
        
        # 6. Update Cache
        analysis_cache[cache_key] = response
        
        return response

    except ProviderSelectionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LLMRateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal processing error")


@app.get("/health")
def health_check():
    return {"status": "ok"}
