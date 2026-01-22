"""
Hugging Face LLM Client

Uses the Hugging Face Router API (OpenAI-compatible) for text generation.
"""

import httpx
from typing import List, Optional
from ...schemas import IssueAnalysis
import logging
import json
import re
import os

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


def _get_api_url() -> str:
    """Get the API URL."""
    custom_endpoint = os.environ.get("HF_INFERENCE_ENDPOINT")
    if custom_endpoint:
        return custom_endpoint
    
    # Default to the global Router URL for Chat Completions
    return "https://router.huggingface.co/v1/chat/completions"


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("No valid JSON found in response")


async def run_huggingface(
    context: str,
    api_key: str,
    model_name: str,
    allowed_labels: Optional[List[str]] = None
) -> IssueAnalysis:
    """
    Run analysis using Hugging Face Router API (OpenAI Compatible).
    """
    url = _get_api_url()
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
        "max_tokens": 500,
        "temperature": 0.3,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # OpenAI format response
            content = result["choices"][0]["message"]["content"]
            
            logger.info(f"HuggingFace raw response: {content[:200]}...")
            
            # Parse JSON
            parsed = _extract_json(content)
            
            return IssueAnalysis(
                summary=parsed.get("summary", "Unable to generate summary"),
                type=parsed.get("type", "other"),
                priority_score=parsed.get("priority_score", "3 - Unable to assess"),
                suggested_labels=parsed.get("suggested_labels", []),
                potential_impact=parsed.get("potential_impact", "Unable to assess")
            )
            
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        logger.error(f"HuggingFace API error: {status} - {e.response.text}")
        if status == 429:
            from ..router import LLMRateLimitError
            raise LLMRateLimitError(
                "Hugging Face rate limit exceeded. The model is currently busy. Please try again later."
            )
        raise RuntimeError(f"HuggingFace API error: {status}")

    except Exception as e:
        logger.error(f"HuggingFace error: {e}")
        raise RuntimeError(f"HuggingFace error: {e}")


async def verify_model(api_key: str, model_name: str) -> bool:
    """
    Verify if a model is available and accessible using Chat Completions.
    """
    url = _get_api_url()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step A: Ping
            payload_ping = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
                "max_tokens": 5
            }
            resp_ping = await client.post(url, headers=headers, json=payload_ping)
            
            # Rate limit or payment required - don't mark as available
            if resp_ping.status_code == 429:
                logger.warning(f"HF {model_name} rate limited (Step A) - marking as unavailable")
                return False
            
            if resp_ping.status_code == 402:
                logger.warning(f"HF {model_name} payment required (402) - marking as unavailable")
                return False
                
            if resp_ping.status_code != 200:
                logger.debug(f"HF Step A (Ping) failed {model_name}: {resp_ping.status_code}")
                return False
                
            content_ping = resp_ping.json()["choices"][0]["message"]["content"]
            if "OK" not in content_ping:
                logger.debug(f"HF Step A (Ping) content mismatch: {content_ping}")
                return False

            # Step B: Functional JSON
            payload_json = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Return a JSON object with key hello and value world. Output ONLY JSON."}],
                "max_tokens": 30,
                "response_format": {"type": "json_object"} 
            }
            # Note: response_format is OpenAI spec, HF might support it or strict output. 
            # If HF Inference API doesn't support json_object, we rely on prompt.
            # Most HF models on Router support basic chat.
            
            resp_json = await client.post(url, headers=headers, json=payload_json)
            
            # Rate limit or payment required - don't mark as available
            if resp_json.status_code == 429:
                logger.warning(f"HF {model_name} rate limited (Step B) - marking as unavailable")
                return False
            
            if resp_json.status_code == 402:
                logger.warning(f"HF {model_name} payment required (402) - marking as unavailable")
                return False
                
            if resp_json.status_code != 200:
                logger.debug(f"HF Step B (JSON) failed {model_name}: {resp_json.status_code}")
                return False

            try:
                content_json = resp_json.json()["choices"][0]["message"]["content"]
                # Extract JSON if wrapped in markdown
                match = re.search(r'\{.*\}', content_json, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    data = json.loads(content_json)
                    
                if data.get("hello") != "world":
                    logger.debug(f"HF Step B (JSON) content mismatch: {data}")
                    return False
            except Exception as e:
                logger.debug(f"HF Step B (JSON) parse error {model_name}: {e}")
                return False

            return True

    except Exception as e:
        logger.debug(f"HF model verification failed for {model_name}: {e}")
        return False

