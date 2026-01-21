"""
LLM Provider Registry

Scans environment variables to detect configured LLM API keys and builds
a list of available providers. Supports multiple keys per provider.

Supported providers:
- Gemini: GEMINI_API_KEY, GEMINI_API_KEY_2, ...
- OpenAI: OPENAI_API_KEY, OPENAI_API_KEY_2, ...
- Anthropic/Claude: ANTHROPIC_API_KEY, CLAUDE_API_KEY, ...
- Hugging Face: HF_API_KEY, HUGGINGFACE_API_KEY, HF_TOKEN, ...
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
    provider: str        # Provider type: "gemini", "openai", "anthropic", "huggingface"
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
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
    # Note: HF model must be available on Serverless Inference API
    # See: https://huggingface.co/docs/api-inference/supported-models
    "huggingface": os.getenv("HF_MODEL", "google/gemma-2-2b-it"),
}




# Placeholder patterns to filter out (case-insensitive)
PLACEHOLDER_PATTERNS = [
    r"^your_.*_here$",
    r"^sk-your.*$",
    r"^your-.*-key.*$",
    r"^placeholder.*$",
    r"^xxx+$",
    r"^test.*key.*$",
]


def _is_placeholder(value: str) -> bool:
    """Check if a value looks like a placeholder API key."""
    if not value:
        return True
    value_lower = value.lower().strip()
    if len(value_lower) < 10:  # API keys are usually longer
        return True
    for pattern in PLACEHOLDER_PATTERNS:
        if re.match(pattern, value_lower):
            return True
    return False


def _scan_env_for_keys(prefixes: List[str]) -> List[tuple]:
    """
    Scan environment variables for API keys matching patterns.
    Returns list of (suffix_number, api_key) tuples.
    
    Supports multiple prefix patterns for backwards compatibility.
    
    Examples:
        GEMINI_API_KEY -> (1, "key_value")
        GEMINI_API_KEY_2 -> (2, "key_value")
        HF_API_KEY -> (1, "key_value")
        HF_TOKEN -> (1, "key_value")
    """
    results = []
    seen_nums = set()
    
    for prefix in prefixes:
        # Pattern for PREFIX_API_KEY or PREFIX_API_KEY_N
        api_key_pattern = re.compile(rf"^{prefix}_API_KEY(_(\\d+))?$", re.IGNORECASE)
        # Pattern for PREFIX_TOKEN (common for HF)
        token_pattern = re.compile(rf"^{prefix}_TOKEN$", re.IGNORECASE)
        
        for key, value in os.environ.items():
            if _is_placeholder(value):
                continue
                
            # Check API_KEY pattern
            match = api_key_pattern.match(key)
            if match and value:
                suffix = match.group(2)
                num = int(suffix) if suffix else 1
                if num not in seen_nums:
                    results.append((num, value))
                    seen_nums.add(num)
                continue
            
            # Check TOKEN pattern
            if token_pattern.match(key) and value:
                num = 1
                if num not in seen_nums:
                    results.append((num, value))
                    seen_nums.add(num)
    
    return sorted(results, key=lambda x: x[0])


def _get_label(provider: str, index: int, total: int) -> str:
    """Generate human-readable label for provider."""
    display_names = {
        "gemini": "Gemini",
        "openai": "OpenAI",
        "anthropic": "Claude",
        "huggingface": "Hugging Face",
    }
    name = display_names.get(provider, provider.capitalize())
    
    if total == 1:
        return name
    else:
        if index == 1:
            return f"{name} (primary)"
        else:
            return f"{name} (key {index})"


def get_available_providers() -> List[LLMProvider]:
    """
    Detect all configured LLM providers from environment variables.
    Returns list of LLMProvider objects.
    
    Only returns providers with valid (non-placeholder) API keys.
    """
    providers = []
    
    # Scan for Gemini keys
    gemini_keys = _scan_env_for_keys(["GEMINI"])
    for num, api_key in gemini_keys:
        providers.append(LLMProvider(
            id=f"gemini_{num}",
            label=_get_label("gemini", num, len(gemini_keys)),
            provider="gemini",
            model=DEFAULT_MODELS["gemini"],
            api_key=api_key,
            is_available=True
        ))
    
    # Scan for OpenAI keys
    openai_keys = _scan_env_for_keys(["OPENAI"])
    for num, api_key in openai_keys:
        providers.append(LLMProvider(
            id=f"openai_{num}",
            label=_get_label("openai", num, len(openai_keys)),
            provider="openai",
            model=DEFAULT_MODELS["openai"],
            api_key=api_key,
            is_available=True
        ))
    
    # Scan for Anthropic/Claude keys
    anthropic_keys = _scan_env_for_keys(["ANTHROPIC", "CLAUDE"])
    for num, api_key in anthropic_keys:
        providers.append(LLMProvider(
            id=f"anthropic_{num}",
            label=_get_label("anthropic", num, len(anthropic_keys)),
            provider="anthropic",
            model=DEFAULT_MODELS["anthropic"],
            api_key=api_key,
            is_available=True
        ))
    
    # Scan for Hugging Face keys
    hf_keys = _scan_env_for_keys(["HF", "HUGGINGFACE"])
    for num, api_key in hf_keys:
        providers.append(LLMProvider(
            id=f"huggingface_{num}",
            label=_get_label("huggingface", num, len(hf_keys)),
            provider="huggingface",
            model=DEFAULT_MODELS["huggingface"],
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
