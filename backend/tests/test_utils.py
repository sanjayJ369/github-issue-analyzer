from app.utils import parse_github_url, truncate_text

def test_parse_github_url_valid():
    assert parse_github_url("https://github.com/owner/repo") == ("owner", "repo")
    assert parse_github_url("github.com/owner/repo") == ("owner", "repo")
    assert parse_github_url("https://www.github.com/owner/repo") == ("owner", "repo")

def test_parse_github_url_git_suffix():
    assert parse_github_url("https://github.com/owner/repo.git") == ("owner", "repo")

def test_parse_github_url_invalid():
    assert parse_github_url("https://gitlab.com/owner/repo") == (None, None)
    assert parse_github_url("https://github.com/owner") == (None, None)

def test_truncate_text_short():
    text = "Short text"
    truncated, is_truncated = truncate_text(text, 100)
    assert truncated == text
    assert is_truncated is False

def test_truncate_text_long():
    text = "A" * 100
    truncated, is_truncated = truncate_text(text, 10)
    assert len(truncated) < 100
    assert "TRUNCATED" in truncated
    assert is_truncated is True
