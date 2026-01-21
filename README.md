# IssueInsight - Agentic GitHub Issue Analyzer

A powerful AI-powered tool that transforms messy GitHub issues into structured engineering insights. Built with **FastAPI** + **React** + **Google Gemini**.

![IssueInsight Demo](https://placehold.co/800x400?text=IssueInsight+-+Analyze+GitHub+Issues+with+AI)

## ✨ Features

- **Structured Analysis**: Summary, classification, priority scoring, and label suggestions
- **Modern UI**: React-based SPA with dark/light theme, responsive design
- **Agentic UX**: Real-time status feed showing analysis pipeline progress
- **Extra Mile Features**:
  - 📋 Copy JSON button for easy export
  - ⚠️ Closed issue warnings
  - 💾 15-minute TTL caching for fast repeat queries
  - 🔄 Intelligent error handling with retry options

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React SPA     │────▶│   FastAPI       │────▶│   GitHub API    │
│   (Vite + TW)   │     │   Backend       │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Google Gemini  │
                        │  (Structured)   │
                        └─────────────────┘
```

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + Vite + Tailwind CSS | Modern, responsive UI |
| Backend | FastAPI + Pydantic | Type-safe API with validation |
| AI/LLM | Google Gemini (JSON Mode) | Structured output generation |
| Data | GitHub REST API + HTTPX | Async data fetching with retries |

---

## 🚀 Quick Start (< 5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key ([Get one free](https://aistudio.google.com/app/apikey))
- (Optional) GitHub Token for higher rate limits

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sanjayJ369/github-issue-analyzer.git
cd github-issue-analyzer

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Start Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. Start Frontend (new terminal)
cd frontend_react
npm install
npm run dev
```

Open http://localhost:5173 and start analyzing!

---

## 📂 Project Structure

```
github-issue-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── github_client.py  # GitHub API integration
│   │   ├── llm_client.py     # Gemini integration
│   │   ├── schemas.py        # Pydantic models
│   │   └── utils.py          # URL parsing, context building
│   ├── tests/
│   │   ├── test_main.py      # Endpoint tests (10 tests)
│   │   └── test_utils.py     # Utility tests (14 tests)
│   └── requirements.txt
├── frontend_react/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api.js            # API client
│   │   └── App.jsx           # Main application
│   └── package.json
├── .github/workflows/
│   └── ci-cd.yml             # GitHub Actions CI
├── vercel.json               # Vercel deployment config
└── README.md
```

---

## 🧠 Prompt Engineering Approach

The LLM prompt is crafted with several key techniques:

### 1. Role Definition
```
"You are an expert engineering assistant..."
```

### 2. Strict Output Requirements
- Enforces `X/5 - Justification` format for priority scores
- Limits labels to standard kebab-case (e.g., `bug`, `enhancement`)
- Uses Gemini's **Structured Output** mode for guaranteed JSON schema

### 3. Context-Aware Label Suggestions
```python
if allowed_labels:
    system_prompt += f"\n\nPrefer using these existing repository labels: {labels_str}"
```
Fetches actual repo labels and includes them in the prompt for relevant suggestions.

### 4. Robustness
- Handles missing issue bodies with `"(No description)"`
- Truncates long comment threads with `[...Remaining N comments truncated...]`
- 24 unit tests covering edge cases

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

**Coverage: 24 tests**
- Health check endpoint
- Success/error scenarios (404, 403, 400, 422)
- Closed issue warnings
- URL parsing edge cases
- Context building with comments
- Truncation behavior

---

## 🔧 Edge Case Handling

| Edge Case | Solution |
|-----------|----------|
| No comments | Empty array handled gracefully |
| Very long threads | Truncated with clear marker in context |
| Closed issues | Warning banner in response |
| Invalid URLs | 400 Bad Request with clear message |
| Rate limits | 403 with "rate limit" detail |
| Missing API key | Graceful startup + clear error on use |

---

## 🌐 Deployment

### Vercel (Production)
The app is configured for Vercel monorepo deployment:
- Frontend: Static build via `@vercel/static-build`
- Backend: Python serverless function via `@vercel/python`
- Environment variables: Set `GEMINI_API_KEY` and `GITHUB_TOKEN` in Vercel dashboard

### GitHub Actions CI
- Runs on every push/PR to `main`
- Executes full test suite
- See `.github/workflows/ci-cd.yml`

---

## 📦 Dependencies

### Backend
```
fastapi, uvicorn, pydantic, httpx, tenacity, cachetools, python-dotenv, google-generativeai
```

### Frontend
```
react, vite, tailwindcss, lucide-react, sonner, react-syntax-highlighter
```

---

## 💡 Extra Mile Features

1. **Copy JSON Button** - One-click export of analysis results
2. **Theme Toggle** - Dark/Light mode with persistence
3. **Agentic Status Feed** - Real-time pipeline visualization
4. **Closed Issue Warning** - Visual alert for stale data
5. **Response Caching** - 15-min TTL for performance
6. **Responsive Design** - Works on mobile, tablet, desktop
7. **Comprehensive Tests** - 24 automated test cases

---

## 📝 License

MIT License - Feel free to use and modify!
