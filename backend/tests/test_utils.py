from app.utils import parse_github_url, truncate_text, build_issue_context


# ============ URL Parsing Tests ============

def test_parse_github_url_valid():
    """Test parsing valid GitHub URLs."""
    assert parse_github_url("https://github.com/owner/repo") == ("owner", "repo")
    assert parse_github_url("github.com/owner/repo") == ("owner", "repo")
    assert parse_github_url("https://www.github.com/owner/repo") == ("owner", "repo")


def test_parse_github_url_git_suffix():
    """Test parsing URL with .git suffix."""
    assert parse_github_url("https://github.com/owner/repo.git") == ("owner", "repo")


def test_parse_github_url_with_paths():
    """Test parsing URLs with additional path segments."""
    assert parse_github_url("https://github.com/fastapi/fastapi/issues/123") == ("fastapi", "fastapi")
    assert parse_github_url("https://github.com/owner/repo/pulls") == ("owner", "repo")


def test_parse_github_url_invalid():
    """Test that non-GitHub URLs return None."""
    assert parse_github_url("https://gitlab.com/owner/repo") == (None, None)
    assert parse_github_url("https://github.com/owner") == (None, None)
    assert parse_github_url("not a url") == (None, None)
    assert parse_github_url("") == (None, None)


def test_parse_github_url_special_characters():
    """Test parsing repos with hyphens and underscores."""
    assert parse_github_url("https://github.com/my-org/my_repo") == ("my-org", "my_repo")
    assert parse_github_url("https://github.com/user123/project-v2") == ("user123", "project-v2")


# ============ Text Truncation Tests ============

def test_truncate_text_short():
    """Test that short text is not truncated."""
    text = "Short text"
    truncated, is_truncated = truncate_text(text, 100)
    assert truncated == text
    assert is_truncated is False


def test_truncate_text_long():
    """Test that long text is truncated with marker."""
    text = "A" * 100
    truncated, is_truncated = truncate_text(text, 10)
    assert len(truncated) < 100
    assert "TRUNCATED" in truncated
    assert is_truncated is True


def test_truncate_text_exact_length():
    """Test text exactly at max length is not truncated."""
    text = "A" * 50
    truncated, is_truncated = truncate_text(text, 50)
    assert truncated == text
    assert is_truncated is False


def test_truncate_text_empty():
    """Test empty text handling."""
    text = ""
    truncated, is_truncated = truncate_text(text, 100)
    assert truncated == ""
    assert is_truncated is False


# ============ Build Issue Context Tests ============

def test_build_issue_context_basic():
    """Test building context from basic issue data."""
    issue = {
        "title": "Test Issue",
        "body": "This is the description.",
        "state": "open",
        "user": {"login": "testuser"}
    }
    comments = []
    
    context = build_issue_context(issue, comments)
    
    assert "Title: Test Issue" in context
    assert "State: open" in context
    assert "Author: testuser" in context
    assert "This is the description." in context


def test_build_issue_context_with_comments():
    """Test building context with comments."""
    issue = {
        "title": "Issue",
        "body": "Body",
        "state": "open",
        "user": {"login": "author"}
    }
    comments = [
        {"body": "First comment", "user": {"login": "user1"}},
        {"body": "Second comment", "user": {"login": "user2"}}
    ]
    
    context = build_issue_context(issue, comments)
    
    assert "First comment" in context
    assert "Comment by user1" in context
    assert "Second comment" in context
    assert "Comment by user2" in context


def test_build_issue_context_no_body():
    """Test handling issue with no body."""
    issue = {
        "title": "No Body Issue",
        "body": None,
        "state": "open",
        "user": {"login": "user"}
    }
    
    context = build_issue_context(issue, [])
    
    assert "No description" in context


def test_build_issue_context_missing_user():
    """Test handling issue with missing user data."""
    issue = {
        "title": "Test",
        "body": "Body",
        "state": "open",
        "user": {}
    }
    
    context = build_issue_context(issue, [])
    
    assert "Author: unknown" in context


def test_build_issue_context_truncates_many_comments():
    """Test that too many comments trigger truncation message."""
    issue = {
        "title": "Popular Issue",
        "body": "This has many comments",
        "state": "open",
        "user": {"login": "author"}
    }
    # Create many long comments
    comments = [
        {"body": "X" * 50000, "user": {"login": f"user{i}"}}
        for i in range(100)
    ]
    
    context = build_issue_context(issue, comments, max_tokens=1000)  # Small limit
    
    assert "truncated" in context.lower()
