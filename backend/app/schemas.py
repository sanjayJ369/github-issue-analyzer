from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class AnalyzeRequest(BaseModel):
    repo_url: str
    issue_number: int

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

class AnalyzeResponse(BaseModel):
    analysis: IssueAnalysis
    meta: AnalyzeResponseMeta
