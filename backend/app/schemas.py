from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class AnalyzeRequest(BaseModel):
    repo_url: str
    issue_number: int
    provider_id: Optional[str] = Field(
        default=None,
        description="LLM provider ID. Required if multiple providers configured. Auto-selects if only one available."
    )

class IssueAnalysis(BaseModel):
    summary: str = Field(description="A concise summary of the issue and its current status.")
    type: Literal["bug", "feature_request", "documentation", "question", "other"] = Field(
        description="The classification of the issue."
    )
    priority_score: str = Field(
        description="A score from 1-5 followed by a hyphen and a justification, e.g., '5 - Critical System Failure'."
    )
    suggested_labels: List[str] = Field(
        description="A list of 2-3 recommended labels for this issue."
    )
    potential_impact: str = Field(description="A brief assessment of the impact if resolved or ignored.")

class AnalyzeResponseMeta(BaseModel):
    issue_url: str
    fetched_comments_count: int
    truncated: bool
    cached: bool = False
    warning: Optional[str] = None
    provider_id: Optional[str] = Field(default=None, description="The LLM provider used for analysis.")

class AnalyzeResponse(BaseModel):
    analysis: IssueAnalysis
    meta: AnalyzeResponseMeta

class LLMProviderResponse(BaseModel):
    """Response schema for /llm/providers endpoint."""
    id: str
    label: str
    provider: str
    model: str
    is_available: bool
