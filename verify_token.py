import requests
import json
import os

def test_success(url, name):
    print(f"Testing {name}: {url}")
    try:
        # FastAPI repo issue #1 is usually a safe bet for a public issue
        payload = {"repo_url": "https://github.com/fastapi/fastapi", "issue_number": 1}
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success! fetched issue:", data.get("meta", {}).get("issue_url"))
            print("Token likely working (or public access active).")
        else:
            print(f"Failed Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
    print("-" * 20)

test_success("http://localhost:8000/analyze", "Valid Repo Token Check")
