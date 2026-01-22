"""
Gemini LLM Client

Provides async function to run analysis using Google Gemini API.
"""

import google.generativeai as genai
from ...schemas import IssueAnalysis
import logging
import json

logger = logging.getLogger(__name__)


async def run_gemini(
    context: str,
    api_key: str,
    model_name: str,
    allowed_labels: list[str] = None
) -> IssueAnalysis:
    """
    Analyze issue context using Gemini API with structured output.
    
    Args:
        context: The issue context text
        api_key: Gemini API key
        model_name: Model to use (e.g., "gemini-2.0-flash")
        allowed_labels: Optional list of repo labels to prefer
        
    Returns:
        IssueAnalysis object with structured analysis
        
    Raises:
        RuntimeError: If API call fails after retry
    """
    # Configure Gemini with the specific API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    system_prompt = (
        "You are an expert engineering assistant. Analyze the GitHub issue provided below. "
        "Output strictly valid JSON matching the required schema. "
        "Be concise but insightful."
    )
    
    if allowed_labels:
        labels_str = ", ".join(allowed_labels[:50])
        system_prompt += f"\n\nPrefer using these existing repository labels if applicable: {labels_str}"
    
    system_prompt += (
        "\n\nOUTPUT REQUIREMENTS:"
        "\n1. priority_score: Must use the format 'X/5 - Justification'. Example: '5/5 - Critical breakage blocks all users'."
        "\n2. suggested_labels: STRICTLY 2-3 labels. Use ONLY standard, lowercase, kebab-case labels."
    )
    
    full_prompt = f"{system_prompt}\n\nISSUE CONTEXT:\n{context}"
    
    # First attempt
    try:
        result = await model.generate_content_async(
            full_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=IssueAnalysis
            )
        )
        return IssueAnalysis.model_validate_json(result.text)
        
    except Exception as first_error:
        logger.warning(f"First Gemini attempt failed: {first_error}. Retrying...")
        
        # Retry once
        try:
            result = await model.generate_content_async(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=IssueAnalysis
                )
            )
            return IssueAnalysis.model_validate_json(result.text)
            
        except Exception as retry_error:
            # Check for Rate Limit again
            err_str = str(retry_error)
            if "429" in err_str or "ResourceExhausted" in err_str or "QuotaExceeded" in err_str:
                from ..router import LLMRateLimitError
                raise LLMRateLimitError(
                    "Rate Limit Exceeded. The AI provider is currently busy. Please try again in 30 seconds."
                )

            logger.error(f"Gemini retry also failed: {retry_error}")
            
            # Try to extract raw output for debugging
            raw_output = getattr(result, 'text', str(retry_error)) if 'result' in dir() else str(retry_error)
            raise RuntimeError(f"LLM failed after retry. Raw output: {raw_output[:500]}")


async def verify_model(api_key: str, model_name: str) -> bool:
    """
    Verify if a model is available and accessible with the given API key.
    
    Args:
        api_key: Gemini API key
        model_name: Model name to check
        
    Returns:
        bool: True if model is accessible
    """
    # Configure specifically for this check
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    try:
        # Step A: Basic Ping
        # "Reply with exactly: OK"
        ping_resp = await model.generate_content_async(
            "Reply with exactly: OK", 
            generation_config=genai.GenerationConfig(max_output_tokens=5)
        )
        if not ping_resp.text or "OK" not in ping_resp.text:
            logger.debug(f"Gemini Step A (Ping) failed for {model_name}: {ping_resp.text}")
            return False

        # Step B: Functional JSON Test
        # "Return a JSON object with key hello and value world. Output ONLY JSON."
        json_resp = await model.generate_content_async(
            "Return a JSON object with key hello and value world. Output ONLY JSON.",
            generation_config=genai.GenerationConfig(
                max_output_tokens=30,
                response_mime_type="application/json"
            )
        )
        
        try:
            data = json.loads(json_resp.text)
            if data.get("hello") != "world":
                logger.debug(f"Gemini Step B (JSON) content mismatch for {model_name}: {data}")
                return False
        except json.JSONDecodeError:
            logger.debug(f"Gemini Step B (JSON) parse error for {model_name}: {json_resp.text}")
            return False
            
        return True
            
    except Exception as e:
        err_str = str(e)
        # Rate limited - return False, don't mark as available
        if "429" in err_str or "ResourceExhausted" in err_str or "QuotaExceeded" in err_str:
            logger.warning(f"Gemini {model_name} rate limited during verification - marking as rate_limited")
            return False  # Don't mark as available - it's rate limited
            
        logger.debug(f"Gemini model verification failed for {model_name}: {e}")
        return False
