"""
OpenAI LLM Client

Uses the OpenAI API via HTTPX (REST) to avoid extra dependencies.
"""

import httpx
from typing import List, Optional
from ...schemas import IssueAnalysis
import logging
import json
import re

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert software engineering assistant analyzing GitHub issues.
Your task is to analyze the given GitHub issue and provide a structured response.

Respond ONLY with a JSON object in this exact format:
{
    "summary": "A concise 2-3 sentence summary of the issue",
    "type": "bug|feature_request|documentation|question|other",
    "priority_score": "X - Brief justification (where X is 1-5)",
    "suggested_labels": ["label1", "label2"],
    "potential_impact": "Brief assessment of impact"
}

Priority scale:
- 5: Critical (system down, security issue)
- 4: High (major functionality broken)  
- 3: Medium (significant issue)
- 2: Low (minor issue)
- 1: Trivial (cosmetic/minor)"""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("No valid JSON found in response")


async def run_openai(
    context: str,
    api_key: str,
    model_name: str,
    allowed_labels: Optional[List[str]] = None
) -> IssueAnalysis:
    """
    Run analysis using OpenAI API.
    
    Args:
        context: Issue context text
        api_key: OpenAI API key
        model_name: Model name (e.g., "gpt-4o-mini")
        allowed_labels: Optional list of repo labels
        
    Returns:
        IssueAnalysis object
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    user_content = f"GitHub Issue to analyze:\n---\n{context}\n---\n\nRespond with JSON only."
    if allowed_labels:
        user_content += f"\nPrefer these labels: {', '.join(allowed_labels)}"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            logger.info(f"OpenAI raw response: {content[:200]}...")
            
            # Parse JSON
            parsed = json.loads(content)
            
            return IssueAnalysis(
                summary=parsed.get("summary", "Unable to generate summary"),
                type=parsed.get("type", "other"),
                priority_score=parsed.get("priority_score", "3 - Unable to assess"),
                suggested_labels=parsed.get("suggested_labels", []),
                potential_impact=parsed.get("potential_impact", "Unable to assess")
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
        raise RuntimeError(f"OpenAI API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        raise RuntimeError(f"OpenAI error: {e}")


async def verify_model(api_key: str, model_name: str) -> bool:
    """
    Verify if a model is available and accessible with the given API key.
    
    Args:
        api_key: OpenAI API key
        model_name: Model name to check
        
    Returns:
        bool: True if model is accessible
    """
    if "gpt" not in model_name.lower() and "o1" not in model_name.lower():
        # Basic name check
        return False
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Minimal payload for verification
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return True
            
            logger.debug(f"OpenAI verification failed {model_name}: {response.status_code}")
            return False
            
    except Exception as e:
        logger.debug(f"OpenAI model verification failed for {model_name}: {e}")
        return False
