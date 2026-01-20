# GitHub Issue Analyzer

A simple, fast tool to analyze GitHub issues using LLMs. It fetches issue details and comments, then provides a structured analysis including summary, type, priority, and suggested labels.

## Architecture

- **Frontend**: Streamlit (fast UI, easy JSON display)
- **Backend**: FastAPI (clean API, Pydantic validation)
- **GitHub**: Fetch issues + comments via REST API
- **AI**: OpenAI (default) for structured analysis

![Architecture Diagram](https://placehold.co/600x200?text=Streamlit+->+FastAPI+->+GitHub+&+OpenAI)

## Setup (< 5 Minutes)

### Prerequisites
- Python 3.9+
- OpenAI API Key
- (Optional) GitHub Token (for higher rate limits)

### Instructions

1.  **Clone the repository** (if you haven't already)
    ```bash
    git clone <repo_url>
    cd gh_issue_analyzer
    ```

2.  **Configure Environment**
    Copy the example environment file and fill in your keys:
    ```bash
    cp .env.example .env
    # Edit .env and add your OPENAI_API_KEY
    ```

3.  **Start Backend**
    Open a new terminal:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    ```

4.  **Start Frontend**
    Open another terminal:
    ```bash
    cd frontend
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```

5.  **Use the App**
    Open your browser to the URL shown by Streamlit (usually http://localhost:8501).
    Enter a GitHub Issue URL (e.g., `https://github.com/fastapi/fastapi/issues/123`) and click **Analyze**.

## Notes
- **Rate Limiting**: Without a `GITHUB_TOKEN`, you are limited to 60 requests/hour. Add a token to `.env` to increase this.
- **Truncation**: Very long issue threads will be intelligently truncated to fit within LLM context limits.

## Tech Stack
- FastAPI, Uvicorn, Pydantic, HTTPX, Tenacity, Cachetools, OpenAI
- Streamlit, Requests
