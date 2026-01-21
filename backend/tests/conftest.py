"""
Pytest configuration and fixtures for backend tests.
"""

import os
import pytest


@pytest.fixture(autouse=True)
def set_test_env():
    """
    Set test environment variables before each test.
    Ensures only ONE provider is available for auto-selection tests.
    """
    # Store original values
    original_gemini = os.environ.get("GEMINI_API_KEY")
    original_openai = os.environ.get("OPENAI_API_KEY")
    original_gemini_2 = os.environ.get("GEMINI_API_KEY_2")
    
    # Set only one provider key
    os.environ["GEMINI_API_KEY"] = "test_api_key_for_testing"
    
    # Remove any other provider keys to ensure auto-selection works
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY_2", None)
    
    yield
    
    # Restore original values
    if original_gemini:
        os.environ["GEMINI_API_KEY"] = original_gemini
    else:
        os.environ.pop("GEMINI_API_KEY", None)
    
    if original_openai:
        os.environ["OPENAI_API_KEY"] = original_openai
        
    if original_gemini_2:
        os.environ["GEMINI_API_KEY_2"] = original_gemini_2
