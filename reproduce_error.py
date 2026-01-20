import requests
import json

def test_error(url, name):
    print(f"Testing {name}: {url}")
    try:
        payload = {"repo_url": "https://github.com/fastapi/nonexistent", "issue_number": 1}
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    print("-" * 20)

test_error("http://localhost:8000/analyze", "Invalid Repo")
