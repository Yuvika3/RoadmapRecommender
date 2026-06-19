# AI-Powered Career Roadmap Recommender

An industry-grade, full-stack application designed to generate, profile, and track personalized learning paths. The system leverages a hybrid architecture combining machine learning skill profiling (CatBoost Regressors) with generative AI curation (Ollama LLM) to deliver tailored week-by-week study plans.

---

## 🚀 Key Features

* **CatBoost ML Skill Profiling**: Predicts relevance, difficulty, and time feasibility scores for skills dynamically based on career objectives, experience level, and weekly study time.
* **Generative Curation & Fallback**: Leverages local LLMs via Ollama (`qwen2.5:1.5b`) to generate high-fidelity curriculum milestones, learning resources, and mastery criteria. Implements an automatic rule-based fallback system if the local LLM is offline or fails to parse.
* **Interactive Checklist & Progress Metrics**: Saves learning milestone progress in the browser (`localStorage`) and visualizes completion rates in real-time.
* **Sidebar History Workspace**: Persists previously generated learning paths in a local SQLite database for quick access, deletion, and resume.
* **Architectural Test Isolation**: Separate configurations ensure that running backend unit or integration tests operates on a temporary database (`test_roadmap.db`) that is automatically cleaned up, keeping the development database pristine.

---

## 🛠️ Technology Stack

* **Backend**: FastAPI (Python 3.11+), SQLite (database storage), CatBoost (machine learning models), Scikit-learn & Pandas (feature engineering).
* **Frontend**: React 19, Vite 8, Vanilla CSS (Premium Glassmorphic theme).
* **AI Model Runner**: Ollama (model: `qwen2.5:1.5b`).

---

## 📁 Project Directory Structure

```text
RoadMap/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── roadmap.py      # Core endpoints (generate, history, delete)
│   │   │   └── session.py          # SQLite session configuration & test isolation
│   │   └── main.py                 # FastAPI application & server lifespan
│   ├── llm/
│   │   └── ollama_client.py        # Ollama LLM client wrapper & Markdown parser
│   ├── ml/
│   │   ├── fallback/
│   │   │   └── rule_based.py       # Deterministic fallback algorithm
│   │   └── scoring/
│   │       ├── scorer.py           # CatBoost scoring pipeline
│   │       └── *.cbm               # Pre-trained CatBoost model binary files
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── roadmapApi.js       # Frontend API client
│   │   ├── components/
│   │   │   ├── InputForm.jsx       # Goals definition form
│   │   │   ├── Navbar.jsx          # Top navigation bar
│   │   │   └── RoadmapOutput.jsx   # Interactive curriculum & metrics visualization
│   │   ├── pages/
│   │   │   └── Home.jsx            # Layout manager & history sidebar
│   │   ├── styles/
│   │   │   └── global.css          # Glassmorphic layout styling overrides
│   │   ├── App.jsx                 # Page routing entry point
│   │   └── main.jsx                # React bootstrapper
│   └── package.json                # Frontend package dependencies & scripts
└── tests/
    ├── integration/
    │   └── test_api_flow.py        # Backend endpoint and fallback integration tests
    └── unit/
        └── test_scorer.py          # CatBoost feature engineering & scorer unit tests
```

---

## ⚙️ Setup and Installation

### 1. Prerequisites
Ensure you have the following installed on your machine:
* Python 3.11 or higher
* Node.js v18 or higher (with `npm`)
* [Ollama](https://ollama.com/) (installed and running locally)

### 2. Configure Ollama
Pull the required LLM model:
```bash
ollama pull qwen2.5:1.5b
```

### 3. Backend Setup
1. Navigate to the backend directory or root directory:
   ```bash
   # Create a virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend API will be available at `http://127.0.0.1:8000`.

### 4. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The web application will be accessible at `http://localhost:5173`.

---

## 🧪 Running Tests & Validations

### 1. Backend Tests
To run all backend unit and integration tests (isolated from dev database):
```bash
# From workspace root
.venv\Scripts\python.exe -m unittest discover -s tests
```
Or run specific test modules:
```bash
.venv\Scripts\python.exe -m unittest tests/unit/test_scorer.py
.venv\Scripts\python.exe -m unittest tests/integration/test_api_flow.py
```

### 2. Frontend Linter
Ensure 100% clean linter output by running ESLint checks:
```bash
cd frontend
npm run lint
```
