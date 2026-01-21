"""
LLM Provider Registry

Scans environment variables to detect configured LLM API keys and builds
a list of available providers. Supports multiple keys per provider.

Key naming convention:
- GEMINI_API_KEY -> gemini_1
- GEMINI_API_KEY_2 -> gemini_2
- OPENAI_API_KEY -> openai_1
- OPENAI_API_KEY_2 -> openai_2
"""

import os
import re
from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMProvider:
    """Represents a configured LLM provider."""
    id: str              # Stable ID like "gemini_1", "openai_2"
    label: str           # Human-readable label like "Gemini (primary)"
    provider: str        # Provider type: "gemini", "openai"
    model: str           # Model name
    api_key: str         # The actual API key (kept server-side)
    is_available: bool   # Whether the key is valid/set


@dataclass
class LLMProviderInfo:
    """Public-safe provider info (no API key exposed)."""
    id: str
    label: str
    provider: str
    model: str
    is_available: bool


# Default models for each provider
DEFAULT_MODELS = {
    "gemini": os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    "openai": "gpt-4o-mini",
}


def _scan_env_for_keys(prefix: str) -> List[tuple]:
    """
    Scan environment variables for API keys matching pattern.
    Returns list of (suffix_number, api_key) tuples.
    
    Examples:
        GEMINI_API_KEY -> (1, "key_value")
        GEMINI_API_KEY_2 -> (2, "key_value")
    """
    results = []
    pattern = re.compile(rf"^{prefix}_API_KEY(_(\d+))?$")
    
    for key, value in os.environ.items():
        match = pattern.match(key)
        if match and value:
            suffix = match.group(2)
            num = int(suffix) if suffix else 1
            results.append((num, value))
    
    return sorted(results, key=lambda x: x[0])


def _get_label(provider: str, index: int, total: int) -> str:
    """Generate human-readable label for provider."""
    if total == 1:
        return f"{provider.capitalize()}"
    else:
        if index == 1:
            return f"{provider.capitalize()} (primary)"
        else:
            return f"{provider.capitalize()} (key {index})"


def get_available_providers() -> List[LLMProvider]:
    """
    Detect all configured LLM providers from environment variables.
    Returns list of LLMProvider objects.
    """
    providers = []
    
    # Scan for Gemini keys
    gemini_keys = _scan_env_for_keys("GEMINI")
    for num, api_key in gemini_keys:
        providers.append(LLMProvider(
            id=f"gemini_{num}",
            label=_get_label("gemini", num, len(gemini_keys)),
            provider="gemini",
            model=DEFAULT_MODELS["gemini"],
            api_key=api_key,
            is_available=True
        ))
    
    # Scan for OpenAI keys (future support)
    openai_keys = _scan_env_for_keys("OPENAI")
    for num, api_key in openai_keys:
        providers.append(LLMProvider(
            id=f"openai_{num}",
            label=_get_label("openai", num, len(openai_keys)),
            provider="openai",
            model=DEFAULT_MODELS["openai"],
            api_key=api_key,
            is_available=True
        ))
    
    logger.info(f"Detected {len(providers)} LLM provider(s): {[p.id for p in providers]}")
    return providers


def get_provider_info_list() -> List[LLMProviderInfo]:
    """
    Get public-safe list of providers (without API keys).
    This is what gets sent to the frontend.
    """
    return [
        LLMProviderInfo(
            id=p.id,
            label=p.label,
            provider=p.provider,
            model=p.model,
            is_available=p.is_available
        )
        for p in get_available_providers()
    ]


def get_provider_by_id(provider_id: str) -> Optional[LLMProvider]:
    """Get a specific provider by its ID."""
    providers = get_available_providers()
    for p in providers:
        if p.id == provider_id:
            return p
    return None


def get_default_provider() -> Optional[LLMProvider]:
    """Get the first available provider (for auto-selection)."""
    providers = get_available_providers()
    return providers[0] if providers else None
