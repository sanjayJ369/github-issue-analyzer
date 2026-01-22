# IssueInsight - Agentic GitHub Issue Analyzer

A powerful AI-powered tool that transforms messy GitHub issues into structured engineering insights. Built with **FastAPI** + **React** + **Google Gemini**.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://github-issue-analyzer-smoky.vercel.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/sanjayJ369/github-issue-analyzer/)

## ✨ Features

- **Auto-Detection LLM Providers**: Dynamically detects API keys from `.env` and verifies availability
- **Latency Measurement**: Real response time measurement for each model with performance labels
- **Rate-Limit Handling**: Automatic fallback to next available provider on 429 errors
- **Structured Analysis**: Summary, classification, priority scoring, and label suggestions
- **Multi-Provider Support**: Gemini, OpenAI, Anthropic, and Hugging Face
- **Modern UI**: React-based SPA with dark/light theme, responsive design
- **Agentic UX**: Real-time status feed showing analysis pipeline progress

### Extra Features
- 📋 Copy JSON button for easy export
- ⚠️ Closed issue warnings
- 💾 15-minute TTL caching for fast repeat queries
- 🔄 Intelligent error handling with retry options
- 🔀 Provider selection with localStorage persistence
- ⏱️ Latency-based speed indicators (Fast/Medium/Slow)

---

## 🌐 Live Demo

**Try it now**: [https://github-issue-analyzer-smoky.vercel.app/](https://github-issue-analyzer-smoky.vercel.app/)

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
                        │  LLM Providers  │
                        │  (Auto-Detect)  │
                        └─────────────────┘
```

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + Vite + Tailwind CSS | Modern, responsive UI |
| Backend | FastAPI + Pydantic | Type-safe API with validation |
| AI/LLM | Gemini, OpenAI, Anthropic, HuggingFace | Multi-provider support with auto-detection |
| Data | GitHub REST API + HTTPX | Async data fetching with retries |

---

## 🚀 Quick Start (< 5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- At least one LLM API Key:
  - [Google Gemini](https://aistudio.google.com/app/apikey) (free)
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Anthropic](https://console.anthropic.com/)
  - [Hugging Face](https://huggingface.co/settings/tokens)
- (Optional) GitHub Token for higher rate limits

---

### 🐧 Linux / macOS Installation

```bash
# 1. Clone the repository
git clone https://github.com/sanjayJ369/github-issue-analyzer.git
cd github-issue-analyzer

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Start Backend (Terminal 1)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. Start Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

---

### 🪟 Windows Installation

```powershell
# 1. Clone the repository
git clone https://github.com/sanjayJ369/github-issue-analyzer.git
cd github-issue-analyzer

# 2. Configure environment
copy .env.example .env
# Open .env in notepad and add your API keys

# 3. Start Backend (Terminal 1 - PowerShell)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 4. Start Frontend (Terminal 2 - PowerShell)
cd frontend
npm install
npm run dev
```

> **Note for Windows**: If you encounter execution policy errors, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### ✅ Verify Installation

1. Backend API: http://localhost:8000/docs (Swagger UI)
2. Frontend App: http://localhost:5173
3. Try analyzing: `https://github.com/fastapi/fastapi/issues/1`

---

## 🔑 Environment Variables

```bash
# LLM Providers (at least one required)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
HF_API_KEY=your_huggingface_key

# Optional
GITHUB_TOKEN=your_github_token  # Higher rate limits
MODEL_NAME=gemini-2.0-flash     # Default model
```

The app will auto-detect which providers are available and verify them with real LLM calls.

---

## 📂 Project Structure

```
github-issue-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── github_client.py  # GitHub API integration
│   │   ├── llm/
│   │   │   ├── providers.py  # Auto-detection & latency measurement
│   │   │   ├── router.py     # Provider routing with fallback
│   │   │   └── clients/      # Provider-specific clients
│   │   ├── schemas.py        # Pydantic models
│   │   └── utils.py          # URL parsing, context building
│   ├── tests/                # 11 test cases
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api.js            # API client
│   │   └── App.jsx           # Main application
│   └── package.json
└── vercel.json               # Vercel deployment config
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

**11 tests covering:**
- Health check endpoint
- Provider listing with latency
- Success/error scenarios (404, 403, 400, 422)
- Closed issue warnings
- Response structure validation

---

## 🌐 Deployment

### Vercel (Production)
- **Live URL**: [https://github-issue-analyzer-smoky.vercel.app/](https://github-issue-analyzer-smoky.vercel.app/)
- Frontend: Static build via `@vercel/static-build`
- Backend: Python serverless function via `@vercel/python`
- Environment variables: Set API keys in Vercel dashboard

### GitHub Actions CI
- Runs on every push/PR to `main`
- Executes full test suite
- See `.github/workflows/ci-cd.yml`

---

## 💡 Key Features

### LLM Provider Auto-Detection
| Feature | Description |
|---------|-------------|
| 🔍 **Auto-Detection** | Scans `.env` for API keys automatically |
| ⏱️ **Latency Measurement** | Real response time for each model |
| 🏷️ **Speed Labels** | Fast (<1s), Medium (1-3s), Slow (>3s) |
| 🔄 **Rate-Limit Fallback** | Auto-retry with next available provider |
| 🔒 **Concurrency Limiting** | Semaphore-based (max 5 parallel checks) |

### UI/UX Enhancements
| Feature | Description |
|---------|-------------|
| 📋 **Copy JSON Button** | One-click export of analysis results |
| 🌓 **Theme Toggle** | Dark/Light mode with persistence |
| 📱 **Responsive Design** | Adaptive layout for all devices |
| ✨ **Status Feed** | Real-time visualization of pipeline |
| 🎨 **Modern UI** | Glassmorphism effects with animations |

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 🔗 Links

- **Live Demo**: [https://github-issue-analyzer-smoky.vercel.app/](https://github-issue-analyzer-smoky.vercel.app/)
- **GitHub**: [https://github.com/sanjayJ369/github-issue-analyzer/](https://github.com/sanjayJ369/github-issue-analyzer/)
