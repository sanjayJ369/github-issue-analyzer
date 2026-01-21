"""
Anthropic Claude LLM Client

Uses the Anthropic API for Claude models.
"""

import httpx
from typing import List, Optional
from ...schemas import IssueAnalysis
import logging
import json

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


async def run_anthropic(
    context: str,
    api_key: str,
    model_name: str,
    allowed_labels: Optional[List[str]] = None
) -> IssueAnalysis:
    """
    Run analysis using Anthropic Claude API.
    
    Args:
        context: Issue context text
        api_key: Anthropic API key
        model_name: Model name (e.g., "claude-3-5-sonnet-20241022")
        allowed_labels: Optional list of repo labels
        
    Returns:
        IssueAnalysis object
    """
    user_content = f"Analyze this GitHub issue:\n\n{context}"
    
    if allowed_labels:
        user_content += f"\n\nPrefer these labels when applicable: {', '.join(allowed_labels)}"
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    payload = {
        "model": model_name,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": user_content}
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("content", [])
            
            if content and len(content) > 0:
                text = content[0].get("text", "{}")
            else:
                raise RuntimeError("Empty response from Claude")
            
            logger.info(f"Anthropic raw response: {text[:200]}...")
            
            # Parse JSON from response
            parsed = json.loads(text)
            
            return IssueAnalysis(
                summary=parsed.get("summary", "Unable to generate summary"),
                type=parsed.get("type", "other"),
                priority_score=parsed.get("priority_score", "3 - Unable to assess"),
                suggested_labels=parsed.get("suggested_labels", []),
                potential_impact=parsed.get("potential_impact", "Unable to assess")
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Anthropic API error: {e.response.status_code} - {e.response.text}")
        raise RuntimeError(f"Anthropic API error: {e.response.status_code}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Anthropic response as JSON: {e}")
        raise RuntimeError("Failed to parse LLM response")
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        raise RuntimeError(f"Anthropic error: {e}")
