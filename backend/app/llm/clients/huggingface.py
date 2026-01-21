"""
Hugging Face LLM Client

Uses the Hugging Face Inference API for text generation.
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


def _build_prompt(context: str, allowed_labels: Optional[List[str]] = None) -> str:
    """Build the analysis prompt."""
    prompt = f"{SYSTEM_PROMPT}\n\n"
    
    if allowed_labels:
        prompt += f"Prefer these labels when applicable: {', '.join(allowed_labels)}\n\n"
    
    prompt += f"GitHub Issue to analyze:\n---\n{context}\n---\n\nRespond with JSON only:"
    return prompt


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
    Run analysis using Hugging Face Inference API.
    
    Args:
        context: Issue context text
        api_key: Hugging Face API key
        model_name: Model name (e.g., "mistralai/Mistral-7B-Instruct-v0.2")
        allowed_labels: Optional list of repo labels
        
    Returns:
        IssueAnalysis object
    """
    prompt = _build_prompt(context, allowed_labels)
    
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "return_full_text": False,
            "temperature": 0.3,
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            else:
                generated_text = str(result)
            
            logger.info(f"HuggingFace raw response: {generated_text[:200]}...")
            
            # Parse JSON from response
            parsed = _extract_json(generated_text)
            
            return IssueAnalysis(
                summary=parsed.get("summary", "Unable to generate summary"),
                type=parsed.get("type", "other"),
                priority_score=parsed.get("priority_score", "3 - Unable to assess"),
                suggested_labels=parsed.get("suggested_labels", []),
                potential_impact=parsed.get("potential_impact", "Unable to assess")
            )
            
    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        status = e.response.status_code
        logger.error(f"HuggingFace API error: {status} - {error_text}")
        
        if status == 410:
            raise RuntimeError(
                f"HuggingFace model '{model_name}' is no longer available. "
                "Set HF_MODEL env var to a supported model from: "
                "https://huggingface.co/docs/api-inference/supported-models"
            )
        elif status == 503:
            raise RuntimeError(
                f"HuggingFace model '{model_name}' is loading. Please retry in a few seconds."
            )
        else:
            raise RuntimeError(f"HuggingFace API error: {status}")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse HuggingFace response as JSON: {e}")
        raise RuntimeError("Failed to parse LLM response")
    except Exception as e:
        logger.error(f"HuggingFace error: {e}")
        raise RuntimeError(f"HuggingFace error: {e}")
