import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from typing import Dict, Any, List, Optional
import os

GITHUB_API_BASE = "https://api.github.com"

def is_retryable_error(exception):
    """
    Retry on network errors or other unexpected exceptions, 
    but fail immediately on 404 (ValueError) or 403 (RuntimeError).
    """
    if isinstance(exception, ValueError): # 404 Not Found
        return False
    if isinstance(exception, RuntimeError): # 403 Rate Limit
        return False
    return True

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token and token != "optional_but_recommended_for_rate_limits":
            self.headers["Authorization"] = f"Bearer {token}"

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception(is_retryable_error)
    )
    async def fetch_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError("Issue not found")
            if response.status_code == 403:
                raise RuntimeError("GitHub API rate limit exceeded")
                
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        # Fetch up to 100 comments (simple pagination for MVP)
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments?per_page=100"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 404:
                return [] # Should not happen if issue exists, but safe fallback
                
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_labels(self, owner: str, repo: str) -> List[str]:
        # Fetch repo labels to helper suggestions
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/labels?per_page=100"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                labels_data = response.json()
                return [l["name"] for l in labels_data]
            except Exception:
                # Fail gracefully for labels, it's an enhancement
                return []
