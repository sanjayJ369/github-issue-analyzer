"""
OpenAI LLM Client (Future Support)

Placeholder for OpenAI API integration.
"""

from ...schemas import IssueAnalysis
import logging

logger = logging.getLogger(__name__)


async def run_openai(
    context: str,
    api_key: str,
    model_name: str,
    allowed_labels: list[str] = None
) -> IssueAnalysis:
    """
    Analyze issue context using OpenAI API.
    
    NOTE: This is a placeholder for future implementation.
    """
    raise NotImplementedError(
        "OpenAI provider is not yet implemented. "
        "Please use a Gemini provider or contribute an OpenAI implementation."
    )
