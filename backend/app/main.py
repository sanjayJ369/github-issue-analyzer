from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
import asyncio
import logging

import os

# App modules
from .schemas import AnalyzeRequest, AnalyzeResponse, AnalyzeResponseMeta
from .github_client import GitHubClient
from .llm_client import LLMClient
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
    allow_origins=["*"], # Allow all for local dev convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
gh_client = GitHubClient(token=Config.GITHUB_TOKEN)
llm_client = LLMClient()

# Caching: Key = (repo_url, issue_number), Value = AnalyzeResponse
# TTL = 15 minutes (900 seconds)
analysis_cache = TTLCache(maxsize=100, ttl=900)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_issue(request: AnalyzeRequest):
    # 0. Check Cache
    cache_key = (request.repo_url, request.issue_number)
    if cache_key in analysis_cache:
        logger.info(f"Serving cached result for {cache_key}")
        response = analysis_cache[cache_key]
        # Return a copy to safely modify 'cached' meta flag without changing stored obj
        # Pydantic .copy() or model_dump + rebuild
        # Simplest: Just setting cached=True on the return object (if model was mutable)
        # But for correctness, let's reconstruct or use the cached model directly; 
        # API consumer handles 'cached' flag if we want to bubble it up dynamicallly.
        # Ideally we'd store the model, and we can just return it. 
        # To strictly set meta.cached=True for *this* response, we'd need to clone it.
        # For simplicity, we just return the cached object. The client won't know it's cached 
        # unless we explicitly update the meta field on a copy.
        
        # Let's clone to updating cached bit
        cached_resp = response.model_copy(deep=True)
        cached_resp.meta.cached = True
        return cached_resp

    # 1. Parse URL
    owner, repo = parse_github_url(request.repo_url)
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    try:
        # 2. Fetch Data (Parallel fetch for speed)
        # Using gather to fetch issue, comments, and labels concurrently
        issue_task = gh_client.fetch_issue(owner, repo, request.issue_number)
        comments_task = gh_client.fetch_comments(owner, repo, request.issue_number)
        labels_task = gh_client.fetch_labels(owner, repo)
        
        issue_data, comments_data, repo_labels = await asyncio.gather(
            issue_task, comments_task, labels_task, return_exceptions=True
        )
        
        # Check for critical errors (issue_data is required)
        if isinstance(issue_data, Exception):
            raise issue_data # Re-raise to be caught by except block
        
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
        
        # 4. Analyze with LLM
        analysis = await llm_client.analyze_issue(truncated_text, allowed_labels=repo_labels)
        
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
                warning=warning_msg
            )
        )
        
        # 6. Update Cache
        analysis_cache[cache_key] = response
        
        return response

    except ValueError as e:
        # 404 or similar
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        # Rate limits
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.get("/health")
def health_check():
    return {"status": "ok"}
