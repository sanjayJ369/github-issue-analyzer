import re
from typing import Tuple, Optional

def parse_github_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses a GitHub repository URL to extract owner and repo name.
    
    Args:
        url: The GitHub URL string.
        
    Returns:
        A tuple of (owner, repo) if valid, else (None, None).
    """
    # Standard: https://github.com/owner/repo
    # With .git: https://github.com/owner/repo.git
    
    # Regex to capture owner and repo
    # Accepts optional http/https, optional www., github.com/
    # Captures owner (group 1) and repo (group 2)
    # Handles optional .git suffix on repo
    pattern = r"github\.com\/([a-zA-Z0-9\-]+)\/([a-zA-Z0-9\-\._]+)"
    
    match = re.search(pattern, url)
    if not match:
        return None, None
        
    owner = match.group(1)
    repo = match.group(2)
    
    # Remove .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]
        
    return owner, repo

def truncate_text(text: str, max_length: int = 100000) -> Tuple[str, bool]:
    """
    Truncates text to a maximum length to fit constraints.
    
    Args:
        text: The input text.
        max_length: Maximum allowed characters.
        
    Returns:
        Tuple of (truncated_text, is_truncated)
    """
    if len(text) <= max_length:
        return text, False
        
    # Simple truncation for now: keep beginning
    # Could be improved to keep start + end
    return text[:max_length] + "\n...[TRUNCATED]", True

def build_issue_context(
    issue_data: dict, 
    comments_data: list[dict], 
    max_tokens: int = 128000
) -> str:
    """
    Constructs a single text blob from issue and comments for the LLM.
    Roughly estimates token count (chars / 4) to stay safe.
    """
    # Target approx char limit based on max_tokens
    # GPT-4o-mini has 128k context, let's play safe with chars
    char_limit = max_tokens * 3 
    
    title = issue_data.get("title", "")
    body = issue_data.get("body", "") or "(No description)"
    user = issue_data.get("user", {}).get("login", "unknown")
    state = issue_data.get("state", "unknown")
    
    context = f"Title: {title}\nState: {state}\nAuthor: {user}\n\nDescription:\n{body}\n\n"
    
    comments_text = "Comments:\n"
    for i, comment in enumerate(comments_data):
        c_body = comment.get("body", "")
        c_user = comment.get("user", {}).get("login", "unknown")
        
        # Simple stop if we are getting too huge
        if len(context) + len(comments_text) + len(c_body) > char_limit:
            comments_text += f"\n[...Remaining {len(comments_data) - i} comments truncated due to length...]"
            break
            
        comments_text += f"--- Comment by {c_user} ---\n{c_body}\n\n"
        
    return context + comments_text
