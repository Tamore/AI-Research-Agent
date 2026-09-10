# 🔬 AI Academic Research Agent

<p align="center">
  <img src="https://img.shields.io/badge/Ollama-Native-000000?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

> An autonomous multi-step research agent powered natively by **local Ollama LLMs**. It queries academic databases (ArXiv, Semantic Scholar), parses paper PDFs, tracks active professors/labs in target countries (e.g. Japan), maintains a persistent **Research Work Log**, and compiles formal **IEEE / ACM styled LaTeX and PDF research paper drafts**.

---

## ✨ Key Features

- 🏠 **100% Local & Private (Ollama Native):** Powered by local Ollama models (`llama3.2`, `mistral`, `qwen2.5`) for zero-cost, private research synthesis.
- 📑 **Peer-Reviewed Search:** Queries ArXiv and Semantic Scholar APIs directly.
- ⚡ **PDF Extraction:** Extracts methodology, algorithms, and evaluation metrics directly from paper PDFs.
- ⛩️ **Faculty & Lab Radar:** Tracks active professors and research labs in specific target countries (e.g. Japan) along with their latest 2024–2026 breakthroughs.
- 📄 **IEEE / ACM Paper & PDF Compiler:** Converts literature synthesis into formal **IEEE 2-column LaTeX drafts (`.tex`)** and compiles ready-to-read PDF reports.
- 📋 **Persistent Research Work Log:** Saves all session queries, parsed notes, and faculty matches into a structured work log file.
- 🎓 **BibTeX Export:** Generates valid `.bib` reference blocks for Overleaf / LaTeX insertion.
- 🐳 **Docker Ready:** Single command execution with Docker Compose.

---

## 🏗️ Architecture Overview

```text
  [ User Query + Target Region (e.g., "Japan") ]
                       │
                       ▼
┌──────────────────────────────────────────────┐
│           Planner Agent (Ollama)             │ ──( Generates Sub-Queries )
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────┐     ┌───────────────────────┐
│   Academic Scraper   │ ──> │ ArXiv / SemScholar API│
└──────────────────────┘     └───────────────────────┘
           │
           ├────────────────────────────┐
           ▼                            ▼
┌──────────────────────┐    ┌────────────────────────┐
│      PDF Parser      │    │  Faculty & Lab Radar   │
│(Extracts Methodology)│    │(Maps Professors & Labs)│
└──────────────────────┘    └────────────────────────┘
           │                            │
           └──────────────┬─────────────┘
                          ▼
┌──────────────────────────────────────────────┐
│        Synthesizer Agent (Ollama)            │ ──> [ Persistent Work Log ]
└──────────────────────────────────────────────┘
                          │
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
[ Markdown Report & BibTeX ]     [ IEEE / ACM PDF Compiler ]
                                 (Outputs .tex & .pdf paper)
```

---

## 🚀 Quickstart Guide

### 1. Ensure Ollama is Running
Make sure [Ollama](https://ollama.com) is installed and running locally:
```bash
ollama run llama3.2
```

### 2. Clone & Setup Environment
```bash
cd ai_academic_research_agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive Swagger API documentation.

---

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for more details.
