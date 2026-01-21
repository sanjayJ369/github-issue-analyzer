from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from app.main import app, gh_client, llm_client

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_analyze_issue_success():
    # Manual mock override
    original_fetch_issue = gh_client.fetch_issue
    original_fetch_comments = gh_client.fetch_comments
    original_fetch_labels = gh_client.fetch_labels
    original_analyze = llm_client.analyze_issue

    try:
        gh_client.fetch_issue = AsyncMock(return_value={
            "title": "Test Issue",
            "body": "This is a test issue body.",
            "state": "open",
            "html_url": "https://github.com/test/repo/issues/1"
        })
        gh_client.fetch_comments = AsyncMock(return_value=[])
        gh_client.fetch_labels = AsyncMock(return_value=["bug", "enhancement"])
        llm_client.analyze_issue = AsyncMock(return_value={
            "summary": "Short summary",
            "priority_score": 8,
            "impact_classification": "High",
            "justification": "It is a bug",
            "suggested_labels": ["bug"]
        })

        payload = {"repo_url": "https://github.com/test/repo", "issue_number": 1}
        response = client.post("/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["summary"] == "Short summary"
        assert data["meta"]["issue_url"] == "https://github.com/test/repo"
        
    finally:
        # Restore original methods
        gh_client.fetch_issue = original_fetch_issue
        gh_client.fetch_comments = original_fetch_comments
        gh_client.fetch_labels = original_fetch_labels
        llm_client.analyze_issue = original_analyze

@pytest.mark.asyncio
async def test_analyze_issue_not_found():
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
