"""
LLM Router

Routes analysis requests to the correct LLM provider based on provider_id.
Handles auto-selection when only one provider is available.
"""

from typing import Optional
from .providers import get_available_providers, get_provider_by_id, get_default_provider, LLMProvider
from .clients.gemini import run_gemini
from .clients.openai import run_openai
from ..schemas import IssueAnalysis
import logging

logger = logging.getLogger(__name__)


class ProviderSelectionError(Exception):
    """Raised when provider selection fails."""
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
            "No LLM providers configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in environment."
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
    
    # Route to correct client
    logger.info(f"Using provider: {provider.id} ({provider.model})")
    
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
    else:
        raise ProviderSelectionError(f"Unknown provider type: {provider.provider}")
