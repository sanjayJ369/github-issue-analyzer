from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from app.main import app, gh_client, analysis_cache
from app.schemas import IssueAnalysis

client = TestClient(app)


# ============ Health Check Tests ============

def test_health_check():
    """Test that the health endpoint returns OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ============ Provider Endpoint Tests ============

def test_list_providers():
    """Test that /llm/providers returns list of providers."""
    response = client.get("/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least one provider if GEMINI_API_KEY is set
    if len(data) > 0:
        assert "id" in data[0]
        assert "label" in data[0]
        assert "provider" in data[0]
        assert "model" in data[0]


# ============ Analyze Endpoint - Success Cases ============

@patch("app.main.analyze_with_provider")
def test_analyze_issue_success(mock_analyze):
    """Test successful analysis of an open issue."""
    original_fetch_issue = gh_client.fetch_issue
    original_fetch_comments = gh_client.fetch_comments
    original_fetch_labels = gh_client.fetch_labels
    analysis_cache.clear()

    try:
        gh_client.fetch_issue = AsyncMock(return_value={
            "title": "Test Issue",
            "body": "This is a test issue body.",
            "state": "open",
            "html_url": "https://github.com/test/repo/issues/1"
        })
        gh_client.fetch_comments = AsyncMock(return_value=[])
        gh_client.fetch_labels = AsyncMock(return_value=["bug", "enhancement"])
        
        mock_analyze.return_value = IssueAnalysis(
            summary="Short summary",
            type="bug",
            priority_score="4/5 - High priority bug",
            suggested_labels=["bug"],
            potential_impact="Could affect users"
        )

        payload = {"repo_url": "https://github.com/test/repo", "issue_number": 1, "provider_id": "gemini_1"}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        data = response.json()
        assert data["analysis"]["summary"] == "Short summary"
        assert data["analysis"]["type"] == "bug"
        assert data["meta"]["issue_url"] == "https://github.com/test/repo"
        assert data["meta"]["cached"] == False
        assert data["meta"]["warning"] is None
        
    finally:
        gh_client.fetch_issue = original_fetch_issue
        gh_client.fetch_comments = original_fetch_comments
        gh_client.fetch_labels = original_fetch_labels


@patch("app.main.analyze_with_provider")
@patch("app.main.get_available_providers")
def test_analyze_closed_issue_returns_warning(mock_providers, mock_analyze):
    """Test that analyzing a closed issue includes a warning in the response."""
    original_fetch_issue = gh_client.fetch_issue
    original_fetch_comments = gh_client.fetch_comments
    original_fetch_labels = gh_client.fetch_labels
    analysis_cache.clear()
    
    from app.llm.providers import LLMProvider
    mock_providers.return_value = [
        LLMProvider(id="gemini_1", label="Gemini", provider="gemini", 
                    model="gemini-2.0-flash", api_key="test_key", is_available=True)
    ]

    try:
        gh_client.fetch_issue = AsyncMock(return_value={
            "title": "Closed Issue",
            "body": "This issue was resolved.",
            "state": "closed",
            "html_url": "https://github.com/test/repo/issues/2"
        })
        gh_client.fetch_comments = AsyncMock(return_value=[])
        gh_client.fetch_labels = AsyncMock(return_value=[])
        
        mock_analyze.return_value = IssueAnalysis(
            summary="Summary of closed issue",
            type="bug",
            priority_score="2/5 - Low priority",
            suggested_labels=["resolved"],
            potential_impact="None"
        )

        payload = {"repo_url": "https://github.com/test/repo", "issue_number": 2, "provider_id": "gemini_1"}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "closed" in data["meta"]["warning"].lower()
        
    finally:
        gh_client.fetch_issue = original_fetch_issue
        gh_client.fetch_comments = original_fetch_comments
        gh_client.fetch_labels = original_fetch_labels


# ============ Analyze Endpoint - Error Cases ============

def test_analyze_issue_not_found():
    """Test that 404 is returned when issue doesn't exist."""
    original_fetch_issue = gh_client.fetch_issue
    
    try:
        mock_fetch = AsyncMock()
        mock_fetch.side_effect = ValueError("Issue not found")
        gh_client.fetch_issue = mock_fetch

        payload = {"repo_url": "https://github.com/test/repo", "issue_number": 999}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 404
        assert response.json()["detail"] == "Issue not found"
        
    finally:
        gh_client.fetch_issue = original_fetch_issue


def test_analyze_rate_limit_exceeded():
    """Test that 403 is returned when GitHub rate limit is hit."""
    original_fetch_issue = gh_client.fetch_issue
    
    try:
        mock_fetch = AsyncMock()
        mock_fetch.side_effect = RuntimeError("GitHub API rate limit exceeded")
        gh_client.fetch_issue = mock_fetch

        payload = {"repo_url": "https://github.com/test/repo", "issue_number": 1}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 403
        assert "rate limit" in response.json()["detail"].lower()
        
    finally:
        gh_client.fetch_issue = original_fetch_issue


def test_analyze_invalid_github_url():
    """Test that 400 is returned for invalid GitHub URLs."""
    payload = {"repo_url": "https://gitlab.com/owner/repo", "issue_number": 1}
    response = client.post("/analyze", json=payload)

    assert response.status_code == 400
    assert "Invalid GitHub URL" in response.json()["detail"]


def test_analyze_missing_repo_url():
    """Test that 422 is returned when repo_url is missing."""
    payload = {"issue_number": 1}
    response = client.post("/analyze", json=payload)

    assert response.status_code == 422


def test_analyze_missing_issue_number():
    """Test that 422 is returned when issue_number is missing."""
    payload = {"repo_url": "https://github.com/test/repo"}
    response = client.post("/analyze", json=payload)

    assert response.status_code == 422


def test_analyze_invalid_issue_number_type():
    """Test that 422 is returned when issue_number is not an integer."""
    payload = {"repo_url": "https://github.com/test/repo", "issue_number": "abc"}
    response = client.post("/analyze", json=payload)

    assert response.status_code == 422


# ============ Response Structure Tests ============

@patch("app.main.analyze_with_provider")
@patch("app.main.get_available_providers")
def test_response_contains_required_fields(mock_providers, mock_analyze):
    """Test that successful response contains all required fields."""
    original_fetch_issue = gh_client.fetch_issue
    original_fetch_comments = gh_client.fetch_comments
    original_fetch_labels = gh_client.fetch_labels
    analysis_cache.clear()
    
    from app.llm.providers import LLMProvider
    mock_providers.return_value = [
        LLMProvider(id="gemini_1", label="Gemini", provider="gemini", 
                    model="gemini-2.0-flash", api_key="test_key", is_available=True)
    ]

    try:
        gh_client.fetch_issue = AsyncMock(return_value={
            "title": "Test", "body": "Test", "state": "open", "html_url": "https://gh.com/t/r/1"
        })
        gh_client.fetch_comments = AsyncMock(return_value=[{"body": "Comment", "user": {"login": "user1"}}])
        gh_client.fetch_labels = AsyncMock(return_value=["bug"])
        
        mock_analyze.return_value = IssueAnalysis(
            summary="S", type="feature_request", priority_score="3/5 - Medium",
            suggested_labels=["enhancement"], potential_impact="Moderate"
        )

        payload = {"repo_url": "https://github.com/t/r", "issue_number": 1, "provider_id": "gemini_1"}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        
        # Check analysis fields
        assert "analysis" in data
        assert "summary" in data["analysis"]
        assert "type" in data["analysis"]
        assert "priority_score" in data["analysis"]
        assert "suggested_labels" in data["analysis"]
        assert "potential_impact" in data["analysis"]
        
        # Check meta fields
        assert "meta" in data
        assert "issue_url" in data["meta"]
        assert "fetched_comments_count" in data["meta"]
        assert data["meta"]["fetched_comments_count"] == 1
        assert "truncated" in data["meta"]
        assert "cached" in data["meta"]
        assert "provider_id" in data["meta"]
        
    finally:
        gh_client.fetch_issue = original_fetch_issue
        gh_client.fetch_comments = original_fetch_comments
        gh_client.fetch_labels = original_fetch_labels
