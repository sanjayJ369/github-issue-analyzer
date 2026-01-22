"""
LLM Provider Registry

Scans environment variables to detect configured LLM API keys and builds
a list of available providers. Supports multiple keys per provider.

Supported providers:
- Gemini: GEMINI_API_KEY, ...
- OpenAI: OPENAI_API_KEY, ...
- Anthropic: ANTHROPIC_API_KEY, ...
- Hugging Face: HF_API_KEY, ...
"""

import os
import re
import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from collections import Counter
from enum import Enum

# Import client verification functions
from .clients.gemini import verify_model as verify_gemini
from .clients.openai import verify_model as verify_openai
from .clients.anthropic import verify_model as verify_anthropic
from .clients.huggingface import verify_model as verify_huggingface

logger = logging.getLogger(__name__)


class AvailabilityStatus(str, Enum):
    """Status of a provider/model availability."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


# Concurrency settings
CONCURRENCY_LIMIT = 5  # Max parallel verification requests per discovery
VERIFICATION_TIMEOUT = 15.0  # Default timeout per model verification (seconds)


@dataclass
class LLMProvider:
    """Represents a configured LLM provider option."""
    id: str              # Stable ID like "gemini_1_flash"
    label: str           # Human-readable label like "Gemini 1.5 Pro"
    provider: str        # Provider type: "gemini", "openai"...
    model: str           # Model name
    api_key: str         # The actual API key (kept server-side)
    status: AvailabilityStatus = AvailabilityStatus.UNAVAILABLE
    latency_ms: Optional[int] = None  # Measured latency in milliseconds
    speed: str = "Standard"  # Speed indicator: Fast, Medium, Slow, Reasoning
    error_message: Optional[str] = None  # Error details if unavailable
    
    @property
    def is_available(self) -> bool:
        """Backward-compatible availability check."""
        return self.status == AvailabilityStatus.AVAILABLE

@dataclass
class LLMProviderInfo:
    """Public-safe provider info (no API key exposed)."""
    id: str
    label: str
    provider: str
    model: str
    status: AvailabilityStatus
    latency_ms: Optional[int] = None
    speed: str = "Standard"
    error_message: Optional[str] = None
    
    @property
    def is_available(self) -> bool:
        """Backward-compatible availability check."""
        return self.status == AvailabilityStatus.AVAILABLE



# Candidate models to verify for each provider
CANDIDATE_MODELS = {
    "gemini": [
        ("gemini-2.0-flash", "Gemini 2.0 Flash"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
    ],
    "openai": [
        ("gpt-4o", "GPT-4o"),
        ("gpt-4o-mini", "GPT-4o Mini"),
        ("o1-mini", "o1 Mini"),
        ("gpt-4.5-preview", "GPT-4.5 Preview"), 
    ],
    "anthropic": [
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet"),
        ("claude-3-opus-20240229", "Claude 3 Opus"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku"),
    ],
    "huggingface": [
        ("deepseek-ai/DeepSeek-R1", "DeepSeek R1"),
        ("deepseek-ai/DeepSeek-R1-Distill-Llama-8B", "DeepSeek R1 Distill"),
        ("meta-llama/Llama-3.1-8B-Instruct", "Llama 3.1 8B"),
        ("google/gemma-2-2b-it", "Gemma 2 2B"),
        ("microsoft/Phi-3-mini-4k-instruct", "Phi-3 Mini"),
    ]
}

# Placeholder patterns to filter out
PLACEHOLDER_PATTERNS = [
    r"^your_.*_here$", r"^sk-your.*$", r"^your-.*-key.*$", 
    r"^placeholder.*$", r"^xxx+$", r"^test.*key.*$"
]

# Simple in-memory cache for discovered providers
# Note: On serverless (Vercel), this resets on each cold start
DISCOVERY_CACHE_TTL = 60  # Reduced from 300 for faster refresh
_LAST_DISCOVERED: List[LLMProvider] = []
_LAST_DISCOVERY_TIME: float = 0


def _is_placeholder(value: str) -> bool:
    if not value: return True
    val = value.lower().strip()
    if len(val) < 8: return True
    for p in PLACEHOLDER_PATTERNS:
        if re.match(p, val): return True
    return False

def _scan_env_for_keys(prefixes: List[str]) -> List[tuple]:
    results = []
    seen_nums = set()
    for prefix in prefixes:
        api_key_pattern = re.compile(rf"^{prefix}_API_KEY(_(\\d+))?$", re.IGNORECASE)
        token_pattern = re.compile(rf"^{prefix}_TOKEN$", re.IGNORECASE)
        for key, value in os.environ.items():
            if _is_placeholder(value): continue
            match = api_key_pattern.match(key)
            if match and value:
                suffix = match.group(2)
                num = int(suffix) if suffix else 1
                if num not in seen_nums:
                    results.append((num, value))
                    seen_nums.add(num)
                continue
            if token_pattern.match(key) and value:
                num = 1
                if num not in seen_nums:
                    results.append((num, value))
                    seen_nums.add(num)
    return sorted(results, key=lambda x: x[0])


def _get_configured_keys() -> List[dict]:
    """Get list of potential provider configurations from env."""
    configs = []
    
    def add(ptype, keys):
        for num, key in keys:
            configs.append({"type": ptype, "num": num, "key": key})

    add("gemini", _scan_env_for_keys(["GEMINI"]))
    add("openai", _scan_env_for_keys(["OPENAI"]))
    add("anthropic", _scan_env_for_keys(["ANTHROPIC", "CLAUDE"]))
    add("huggingface", _scan_env_for_keys(["HF", "HUGGINGFACE"]))
    
    return configs


def _infer_speed(model_name: str, latency_ms: Optional[int] = None) -> str:
    """
    Infer speed label based on actual latency or model name heuristics.
    
    Latency thresholds:
    - Fast: < 1000ms
    - Medium: 1000-3000ms
    - Slow: > 3000ms
    
    Falls back to model-name heuristics if latency unavailable.
    """
    # Use actual latency if available
    if latency_ms is not None:
        if latency_ms < 1000:
            return "Fast"
        elif latency_ms < 3000:
            return "Medium"
        else:
            return "Slow"
    
    # Fallback to model-name heuristics
    m = model_name.lower()
    if any(x in m for x in ["r1", "o1", "reasoning", "opus"]):
        return "Reasoning"  # Implies slow, reasoning-focused
    if any(x in m for x in ["flash", "haiku", "mini", "nemo", "turbo", "small"]):
        return "Fast"
    if any(x in m for x in ["pro", "sonnet", "gpt-4o", "large"]):
        return "Medium"
    return "Standard"

def _prettify_label(model_name: str, label: str) -> str:
    # If label is generic "Custom Model", try to cleaner name from ID
    if label == "Custom Model":
        # Remove common prefixes
        clean = re.sub(r"^(google|meta-llama|deepseek-ai|microsoft|mistralai)/", "", model_name)
        # Check for specific known IDs to make even nicer
        if "gemini-flash" in clean: clean = "Gemini Flash (Latest)"
        return clean
    return label


async def _verify_candidate(
    config: dict, 
    model_id: str, 
    model_name: str, 
    is_multikey: bool,
    semaphore: asyncio.Semaphore
) -> LLMProvider:
    """
    Verify a single model candidate with latency measurement.
    
    Uses semaphore to limit concurrent verifications.
    Returns LLMProvider with status, latency, and error details.
    """
    ptype = config["type"]
    pnum = config["num"]
    key = config["key"]
    
    status = AvailabilityStatus.UNAVAILABLE
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    
    async with semaphore:
        start_time = time.perf_counter()
        
        try:
            # Call provider-specific verify function
            if ptype == "gemini":
                result = await asyncio.wait_for(
                    verify_gemini(key, model_id),
                    timeout=VERIFICATION_TIMEOUT
                )
            elif ptype == "openai":
                result = await asyncio.wait_for(
                    verify_openai(key, model_id),
                    timeout=VERIFICATION_TIMEOUT
                )
            elif ptype == "anthropic":
                result = await asyncio.wait_for(
                    verify_anthropic(key, model_id),
                    timeout=VERIFICATION_TIMEOUT
                )
            elif ptype == "huggingface":
                result = await asyncio.wait_for(
                    verify_huggingface(key, model_id),
                    timeout=VERIFICATION_TIMEOUT
                )
            else:
                result = (AvailabilityStatus.ERROR, 0, f"Unknown provider: {ptype}")
            
            # Calculate latency
            elapsed = time.perf_counter() - start_time
            latency_ms = int(elapsed * 1000)
            
            # Handle result - can be bool (legacy) or tuple (new format)
            if isinstance(result, bool):
                # Legacy boolean result
                status = AvailabilityStatus.AVAILABLE if result else AvailabilityStatus.UNAVAILABLE
            elif isinstance(result, tuple) and len(result) >= 2:
                # New tuple format: (status, latency_ms, error_message)
                raw_status = result[0]
                if isinstance(raw_status, AvailabilityStatus):
                    status = raw_status
                elif isinstance(raw_status, str):
                    # Handle string-based status from verification functions
                    status_map = {
                        "available": AvailabilityStatus.AVAILABLE,
                        "unavailable": AvailabilityStatus.UNAVAILABLE,
                        "rate_limited": AvailabilityStatus.RATE_LIMITED,
                        "error": AvailabilityStatus.ERROR,
                    }
                    status = status_map.get(raw_status.lower(), AvailabilityStatus.UNAVAILABLE)
                elif isinstance(raw_status, bool):
                    status = AvailabilityStatus.AVAILABLE if raw_status else AvailabilityStatus.UNAVAILABLE
                else:
                    status = AvailabilityStatus.UNAVAILABLE
                    
                if len(result) > 2 and result[2]:
                    error_message = str(result[2])
            else:
                status = AvailabilityStatus.UNAVAILABLE
                
        except asyncio.TimeoutError:
            elapsed = time.perf_counter() - start_time
            latency_ms = int(elapsed * 1000)
            status = AvailabilityStatus.ERROR
            error_message = f"Verification timed out after {VERIFICATION_TIMEOUT}s"
            logger.debug(f"Verification timed out for {model_id}")
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            latency_ms = int(elapsed * 1000)
            error_str = str(e)
            
            # Check for rate limit errors
            if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
                status = AvailabilityStatus.RATE_LIMITED
                error_message = "Rate limit exceeded"
            else:
                status = AvailabilityStatus.ERROR
                error_message = error_str[:100]  # Truncate long errors
            
            logger.debug(f"Verification crashed for {model_id}: {e}")

    # Create a unique ID
    safe_model = model_id.split("/")[-1].replace(".", "").replace("-", "_").lower()
    if len(safe_model) > 20: 
        safe_model = safe_model[:20]
    
    pid = f"{ptype}_{pnum}_{safe_model}"
    
    # Label formatting
    pretty_model = _prettify_label(model_id, model_name)
    
    # Only show Key ID if user has multiple keys for this provider
    label_suffix = f" (Key {pnum})" if is_multikey else ""
    final_label = f"{pretty_model}{label_suffix}"
    
    # Infer speed from latency (if available) or model name
    speed = _infer_speed(model_id, latency_ms if status == AvailabilityStatus.AVAILABLE else None)

    return LLMProvider(
        id=pid,
        label=final_label,
        provider=ptype,
        model=model_id,
        api_key=key,
        status=status,
        latency_ms=latency_ms,
        speed=speed,
        error_message=error_message
    )


async def discover_providers(force_refresh: bool = False) -> List[LLMProvider]:
    """
    Async discovery of available models.
    Scans env keys, then verifies candidate models for each key in parallel.
    Uses caching (TTL 5 mins) and semaphore-based concurrency limiting.
    """
    global _LAST_DISCOVERED, _LAST_DISCOVERY_TIME
    
    # Check cache
    if not force_refresh and _LAST_DISCOVERED and (time.time() - _LAST_DISCOVERY_TIME < DISCOVERY_CACHE_TTL):
        logger.info(f"Returning cached providers ({len(_LAST_DISCOVERED)} found)")
        return _LAST_DISCOVERED

    logger.info("Starting fresh provider discovery...")
    configs = _get_configured_keys()
    
    # Count keys per provider type to handle naming
    type_counts = Counter(c["type"] for c in configs)
    
    # Create semaphore for concurrency limiting
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    tasks = []
    for config in configs:
        ptype = config["type"]
        candidates = CANDIDATE_MODELS.get(ptype, [])
        
        # Env override logic...
        env_model = None
        if ptype == "gemini": env_model = os.getenv("MODEL_NAME")
        elif ptype == "openai": env_model = os.getenv("OPENAI_MODEL")
        elif ptype == "anthropic": env_model = os.getenv("ANTHROPIC_MODEL")
        elif ptype == "huggingface": env_model = os.getenv("HF_MODEL")

        if env_model and not any(c[0] == env_model for c in candidates):
            candidates.append((env_model, "Custom Model"))
            
        is_multikey = type_counts[ptype] > 1

        for model_id, model_name in candidates:
            # Pass semaphore for concurrency control
            tasks.append(_verify_candidate(config, model_id, model_name, is_multikey, semaphore))
            
    if not tasks:
        logger.warning("No provider configurations found to verify.")
        return []
        
    # Gather all results with concurrency limiting via semaphore
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_providers = []
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Provider verification task failed: {r}")
        elif r is not None:
            all_providers.append(r)
    
    # Sort: Available first, then by latency (faster first), then by provider name
    def sort_key(p: LLMProvider):
        # Primary: Available providers come first
        availability_order = {
            AvailabilityStatus.AVAILABLE: 0,
            AvailabilityStatus.RATE_LIMITED: 1,
            AvailabilityStatus.ERROR: 2,
            AvailabilityStatus.UNAVAILABLE: 3,
        }
        avail = availability_order.get(p.status, 3)
        
        # Secondary: Lower latency first (use 99999 if None)
        latency = p.latency_ms if p.latency_ms is not None else 99999
        
        # Tertiary: Provider name, then label
        return (avail, latency, p.provider, p.label)
    
    all_providers.sort(key=sort_key)
    
    # Log results
    available_count = sum(1 for p in all_providers if p.is_available)
    logger.info(f"Discovery complete. Found {available_count} available, {len(all_providers)} total providers:")
    for p in all_providers:
        latency_str = f"{p.latency_ms}ms" if p.latency_ms else "N/A"
        logger.info(f" - {p.id}: {p.label} [{p.status.value}] ({latency_str})")
    
    # Update cache
    _LAST_DISCOVERED = all_providers
    _LAST_DISCOVERY_TIME = time.time()
    
    return all_providers


def get_available_providers() -> List[LLMProvider]:
    """
    Synchronous accessor for providers. 
    Returns the last discovered list (filters to only available).
    """
    if _LAST_DISCOVERED:
        return _LAST_DISCOVERED
        
    # Fallback: Just assume first candidate works for each key (legacy behavior)
    fallback = []
    configs = _get_configured_keys()
    for config in configs:
        ptype = config["type"]
        candidates = CANDIDATE_MODELS.get(ptype, [])
        if candidates:
            model_id, model_name = candidates[0]
            
            # Check for env override
            env_model = None
            if ptype == "gemini": env_model = os.getenv("MODEL_NAME")
            elif ptype == "openai": env_model = os.getenv("OPENAI_MODEL")
            elif ptype == "anthropic": env_model = os.getenv("ANTHROPIC_MODEL")
            elif ptype == "huggingface": env_model = os.getenv("HF_MODEL")
            
            if env_model: model_id = env_model
            
            # Create consistent ID format (same as discovered providers)
            safe_model = model_id.split("/")[-1].replace(".", "").replace("-", "_").lower()
            if len(safe_model) > 20: 
                safe_model = safe_model[:20]
            pid = f"{ptype}_{config['num']}_{safe_model}"
            
            fallback.append(LLMProvider(
                id=pid,
                label=f"{model_name}",
                provider=ptype,
                model=model_id,
                api_key=config['key'],
                status=AvailabilityStatus.AVAILABLE,  # Assume available in fallback
                speed="Standard"
            ))
    return fallback


def get_provider_info_list() -> List[LLMProviderInfo]:
    """Public info list (no API keys exposed)."""
    return [
        LLMProviderInfo(
            id=p.id, 
            label=p.label, 
            provider=p.provider, 
            model=p.model, 
            status=p.status,
            latency_ms=p.latency_ms,
            speed=p.speed,
            error_message=p.error_message
        )
        for p in get_available_providers()
    ]


def get_provider_by_id(provider_id: str) -> Optional[LLMProvider]:
    # Check both last discovered and fallback
    for p in get_available_providers():
        if p.id == provider_id: return p
    return None

def get_default_provider() -> Optional[LLMProvider]:
    providers = get_available_providers()
    return providers[0] if providers else None
