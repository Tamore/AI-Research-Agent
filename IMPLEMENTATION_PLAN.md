# 🛠️ Technical Implementation Plan
# AI Academic Research Agent

> **Author:** Nirmiti R. Tamore  
> **Target Directory:** `ai_academic_research_agent/`  
> **Status:** Draft / Ready for Development  

---

## 🏗️ 1. System Components & Project Structure

```text
ai_academic_research_agent/
├── PRD.md                       # Product Requirements Document
├── IMPLEMENTATION_PLAN.md       # Technical Implementation Plan (This file)
├── README.md                    # Public GitHub Repository Documentation
├── requirements.txt             # Python dependencies (Ollama, FastAPI, pdfplumber, WeasyPrint)
├── Dockerfile                   # Single-container execution setup
├── docker-compose.yml           # Container orchestration
├── config.py                    # Environment variables & Ollama config
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── ollama_client.py     # Local Ollama LLM wrapper (http://localhost:11434)
│   │   ├── planner.py           # Sub-query decomposition agent
│   │   ├── scraper.py           # ArXiv & Semantic Scholar fetcher
│   │   ├── pdf_parser.py        # PDF text & table extractor
│   │   ├── faculty_radar.py    # Faculty, Lab & Regional Research Tracker
│   │   ├── logger_agent.py      # Persistent Research Work Log manager
│   │   └── synthesizer.py       # Literature report & IEEE draft synthesizer
│   ├── compilers/
│   │   ├── __init__.py
│   │   ├── ieee_template.py     # IEEE 2-column LaTeX template builder
│   │   └── pdf_exporter.py      # WeasyPrint / ReportLab PDF compiler
│   ├── models/
│   │   └── schemas.py           # Pydantic data schemas (Paper, Query, Faculty, Report)
│   └── utils/
│       ├── arxiv_client.py      # ArXiv API wrapper
│       ├── s2_client.py         # Semantic Scholar API wrapper
│       └── bibtex_builder.py    # BibTeX formatting utility
└── tests/
    ├── test_ollama.py
    ├── test_faculty_radar.py
    └── test_pdf_exporter.py
```

---

## ⚡ 2. Implementation Phasing & Roadmap

### Phase 1: Local Ollama & API Scraper Setup (Week 1)
- Setup Python `venv` and `requirements.txt` (`fastapi`, `uvicorn`, `arxiv`, `pdfplumber`, `pydantic`, `ollama`, `weasyprint`).
- Implement `ollama_client.py` connecting to local Ollama instance (`http://localhost:11434`).
- Implement `arxiv_client.py` and `s2_client.py` for metadata and citation fetching.

### Phase 2: PDF Parsing, Faculty Radar & Work Logger (Week 1 - 2)
- Build `pdf_parser.py` using `pdfplumber` to extract abstract, methodology, and evaluation sections.
- Build `faculty_radar.py`: Filters paper authors by targeted country/region (e.g. *Japan*, *Imperial Universities*).
- Build `logger_agent.py`: Maintains `research_log.json` to store past search queries, paper summaries, and professor discoveries.

### Phase 3: Multi-Agent Synthesis Engine (Week 2)
- Implement `planner.py`: Deconstructs topic into sub-queries.
- Implement `synthesizer.py`: Uses local Ollama model to generate Markdown literature reviews, comparison matrices, and section drafts.

### Phase 4: IEEE LaTeX & PDF Paper Compiler (Week 2 - 3)
- Build `ieee_template.py` and `pdf_exporter.py`: Formats report into an IEEE double-column LaTeX layout (`.tex`) and compiles it into a clean `.pdf` file.
- Construct FastAPI endpoint `POST /api/v1/research` returning JSON, Markdown, IEEE `.pdf`, and `.bib` citation exports.

---

## 📋 3. Pydantic Data Models (`schemas.py`)

```python
from pydantic import BaseModel
from typing import List, Optional

class ResearchQuery(BaseModel):
    topic: str
    target_region: Optional[str] = "Japan"  # e.g., "Japan", "USA", "Europe"
    use_ollama: bool = True                 # Default to local Ollama LLM
    ollama_model: str = "llama3.2"         # e.g., "llama3.2", "mistral", "qwen2.5"
    max_papers: int = 5
    generate_ieee_pdf: bool = True
    export_bibtex: bool = True

class PaperMetadata(BaseModel):
    title: str
    authors: List[str]
    year: int
    arxiv_id: Optional[str] = None
    pdf_url: str
    abstract: str
    extracted_text: Optional[str] = None

class FacultyProfile(BaseModel):
    name: str
    university_or_lab: str
    country: str
    primary_research_focus: str
    latest_paper_title: str
    latest_paper_year: int
    breakthrough_summary: str
    alignment_score: float

class ResearchReport(BaseModel):
    topic: str
    target_region: Optional[str]
    summary_markdown: str
    literature_matrix: str
    faculty_radar: List[FacultyProfile]
    bibtex_citations: str
    ieee_tex_code: str
    pdf_download_url: Optional[str] = None
    analyzed_papers: List[PaperMetadata]
```

---

## 🔒 4. Deployment & Environment Configuration

- **Environment Variables (`.env`):**
  - `OLLAMA_BASE_URL`: `http://localhost:11434`
  - `OLLAMA_DEFAULT_MODEL`: `llama3.2`
  - `GEMINI_API_KEY`: (Optional fallback) API key for Gemini 1.5 Pro / Flash.
  - `MAX_CONCURRENT_SCRAPES`: Default `5`.
