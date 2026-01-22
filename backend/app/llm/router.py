"""
LLM Router

Routes analysis requests to the correct LLM provider based on provider_id.
Handles auto-selection when only one provider is available.

Supported providers:
- gemini: Google Gemini API
- openai: OpenAI API
- anthropic: Anthropic Claude API
- huggingface: Hugging Face Inference API
"""

from typing import Optional
from .providers import get_available_providers, get_provider_by_id, get_default_provider, LLMProvider
from .clients.gemini import run_gemini
from .clients.openai import run_openai
from .clients.anthropic import run_anthropic
from .clients.huggingface import run_huggingface
from ..schemas import IssueAnalysis
import logging

logger = logging.getLogger(__name__)


class ProviderSelectionError(Exception):
    """Raised when provider selection fails."""
    pass

class LLMRateLimitError(Exception):
    """Raised when the LLM provider returns a URL/Quota error (429)."""
    pass


async def analyze_with_provider(
    provider_id: Optional[str],
    context: str,
    allowed_labels: list[str] = None
) -> IssueAnalysis:
    """
    Route analysis request to the appropriate LLM provider.
    
    Args:
        provider_id: Optional provider ID. If None, auto-selects if only 1 provider exists.
        context: Issue context text
        allowed_labels: Optional list of repo labels
        
    Returns:
        IssueAnalysis object
        
    Raises:
        ProviderSelectionError: If provider selection fails
        RuntimeError: If LLM call fails
    """
    providers = get_available_providers()
    
    # No providers configured
    if not providers:
        raise ProviderSelectionError(
            "No LLM providers configured. Please set an API key (GEMINI_API_KEY, OPENAI_API_KEY, "
            "ANTHROPIC_API_KEY, or HF_API_KEY) in your environment."
        )
    
    # Determine which provider to use
    provider: Optional[LLMProvider] = None
    
    if provider_id:
        # Explicit selection
        provider = get_provider_by_id(provider_id)
        if not provider:
            raise ProviderSelectionError(
                f"Invalid provider_id '{provider_id}'. Available: {[p.id for p in providers]}"
            )
    elif len(providers) == 1:
        # Auto-select single provider
        provider = providers[0]
        logger.info(f"Auto-selected provider: {provider.id}")
    else:
        # Multiple providers, no selection made
        raise ProviderSelectionError(
            f"Multiple LLM providers available. Please specify provider_id. "
            f"Available: {[p.id for p in providers]}"
        )
    
    # Route to correct client with rate-limit fallback
    return await _execute_with_fallback(provider, providers, context, allowed_labels)


async def _call_provider(
    provider: LLMProvider,
    context: str,
    allowed_labels: list[str] = None
) -> "IssueAnalysis":
    """Execute LLM call for a specific provider."""
    logger.info(f"Calling provider: {provider.id} ({provider.model})")
    
    if provider.provider == "gemini":
        return await run_gemini(
            context=context,
            api_key=provider.api_key,
            model_name=provider.model,
            allowed_labels=allowed_labels
        )
    elif provider.provider == "openai":
        return await run_openai(
            context=context,
            api_key=provider.api_key,
            model_name=provider.model,
            allowed_labels=allowed_labels
        )
    elif provider.provider == "anthropic":
        return await run_anthropic(
            context=context,
            api_key=provider.api_key,
            model_name=provider.model,
            allowed_labels=allowed_labels
        )
    elif provider.provider == "huggingface":
        return await run_huggingface(
            context=context,
            api_key=provider.api_key,
            model_name=provider.model,
            allowed_labels=allowed_labels
        )
    else:
        raise ProviderSelectionError(f"Unknown provider type: {provider.provider}")


async def _execute_with_fallback(
    primary_provider: LLMProvider,
    all_providers: list[LLMProvider],
    context: str,
    allowed_labels: list[str] = None,
    max_fallback_attempts: int = 2
) -> "IssueAnalysis":
    """
    Execute LLM call with automatic fallback on rate-limit errors.
    
    If the primary provider returns a 429/rate-limit error, tries the next
    available provider from the sorted list.
    """
    from .providers import update_provider_status, AvailabilityStatus
    
    current_provider = primary_provider
    attempted_providers = {primary_provider.id}
    
    try:
        return await _call_provider(current_provider, context, allowed_labels)
        
    except LLMRateLimitError as e:
        # Mark current provider as rate limited in cache
        logger.warning(f"Provider {current_provider.id} rate limited: {e}")
        update_provider_status(
            current_provider.id, 
            AvailabilityStatus.RATE_LIMITED, 
            "Rate limit exceeded during analysis"
        )
        
        # Try fallbacks
        remaining_providers = [
            p for p in all_providers 
            if p.id not in attempted_providers and p.status.value == 'available'
        ]
        
        # Sort by speed/priority? They are already sorted by discover_providers
        
        for i in range(min(len(remaining_providers), max_fallback_attempts)):
            fallback_provider = remaining_providers[i]
            logger.info(f"Falling back to provider: {fallback_provider.id}")
            attempted_providers.add(fallback_provider.id)
            
            try:
                return await _call_provider(fallback_provider, context, allowed_labels)
            except LLMRateLimitError as fe:
                # Mark fallback as rate limited too
                logger.warning(f"Fallback provider {fallback_provider.id} rate limited: {fe}")
                update_provider_status(
                    fallback_provider.id, 
                    AvailabilityStatus.RATE_LIMITED, 
                    "Rate limit exceeded during fallback"
                )
                continue  # Try next fallback
            except Exception as fe:
                # Other errors on fallback - log and continue to next
                logger.error(f"Fallback provider {fallback_provider.id} failed: {fe}")
                continue
                
        # If we exhausted fallbacks or none available, re-raise the original error
        raise LLMRateLimitError(
                    f"Rate limit exceeded for {primary_provider.id}. "
                    f"Tried {len(attempted_providers)} provider(s). Please try again later."
                )
    
    # Should not reach here, but just in case

