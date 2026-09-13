import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from app.models.schemas import ResearchQuery, ResearchReport
from app.agents.ollama_client import OllamaClient
from app.agents.planner import PlannerAgent
from app.agents.pdf_parser import PDFParser
from app.agents.faculty_radar import FacultyRadar
from app.agents.synthesizer import SynthesizerAgent
from app.agents.logger_agent import LoggerAgent
from app.compilers.ieee_template import IEEETemplateBuilder
from app.compilers.pdf_exporter import PDFExporter
from app.utils.arxiv_client import ArXivClient
from app.utils.bibtex_builder import BibTeXBuilder

app = FastAPI(
    title="AI Academic Research Agent API",
    description="Autonomous literature review, faculty radar, and IEEE paper compiler engine.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.agents.hybrid_engine import HybridLLMEngine

ollama = OllamaClient()
hybrid_engine = HybridLLMEngine()
arxiv_client = ArXivClient()
planner = PlannerAgent(ollama_client=ollama)
faculty_radar = FacultyRadar()
synthesizer = SynthesizerAgent(ollama_client=ollama)
logger_agent = LoggerAgent()

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("app/templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>CiteX Online</h1>"

@app.get("/health")
async def health_check():
    status = await hybrid_engine.check_status()
    return {
        "status": "healthy",
        "engine": status,
        "ollama_connected": False,
        "local_intel_connected": True
    }

@app.post("/api/v1/engine/switch")
def switch_engine(payload: dict):
    mode = payload.get("mode", "auto")
    api_key = payload.get("groq_api_key", "")
    hybrid_engine.set_mode(mode, api_key)
    return {"status": "updated", "mode": mode}

@app.get("/api/v1/notes/folders")
def get_notes_folders():
    """Retrieve all research notes organized by topic folder."""
    return logger_agent.get_notes_by_folder()

@app.get("/api/v1/papers")
def get_generated_papers():
    """Retrieve catalog of all compiled IEEE draft papers."""
    return logger_agent.get_generated_papers()

@app.get("/api/v1/history")
def get_research_history():
    """Retrieve persistent research session log history."""
    return logger_agent.get_history()

@app.post("/api/v1/notes")
def save_research_note(note_data: dict):
    """Save an active tab / paper note into persistent research_log.json with folder categorization."""
    title = note_data.get("title", "Untitled Research Note")
    url = note_data.get("url", "")
    note_text = note_data.get("note", "")
    folder = note_data.get("folder", "General Research")
    entry = logger_agent.log_note(title=title, url=url, note_text=note_text, folder=folder)
    return {"status": "saved", "entry": entry}

@app.get("/api/v1/download-pdf")
def download_pdf(filepath: str = "ieee_paper_draft.pdf"):
    """Download compiled IEEE PDF paper draft."""
    try:
        return FileResponse(filepath, media_type="application/pdf", filename=filepath)
    except Exception as e:
        raise HTTPException(status_code=404, detail="PDF file not found.")

@app.post("/api/v1/research", response_model=ResearchReport)
async def execute_research(query: ResearchQuery, background_tasks: BackgroundTasks):
    """Execute complete multi-step autonomous research pipeline."""
    try:
        # Step 1: Query decomposition via Planner Agent
        subqueries = await planner.generate_subqueries(query.topic, count=2)
        
        # Step 2: Academic scraping via ArXiv Client
        all_papers = []
        seen_ids = set()
        
        search_terms = [query.topic] + subqueries
        for term in search_terms:
            found = arxiv_client.search_papers(term, max_results=query.max_papers)
            for p in found:
                if p.arxiv_id not in seen_ids:
                    seen_ids.add(p.arxiv_id)
                    all_papers.append(p)
                if len(all_papers) >= query.max_papers:
                    break
            if len(all_papers) >= 1:
                # We have valid context papers, proceed immediately to analysis
                break
                
        papers_to_analyze = all_papers[:query.max_papers]

        # Step 3: Faculty Radar mapping
        faculty_matches = await faculty_radar.scan_faculty(papers_to_analyze, target_region=query.target_region)

        # Step 4: Synthesize Literature Report & Matrix
        report = await synthesizer.generate_report(
            topic=query.topic,
            papers=papers_to_analyze,
            faculty=faculty_matches,
            target_region=query.target_region
        )

        # Step 5: IEEE LaTeX & PDF Paper Compilation
        if query.generate_ieee_pdf:
            tex_code = IEEETemplateBuilder.build_tex(report)
            pdf_filename = f"ieee_paper_draft.pdf"
            PDFExporter.compile_pdf(report, output_filepath=pdf_filename)
            report.ieee_tex_code = tex_code
            report.pdf_download_url = f"/api/v1/download-pdf?filepath={pdf_filename}"

        # Step 6: Persistent Work Log (Background task)
        background_tasks.add_task(
            logger_agent.log_session,
            topic=query.topic,
            target_region=query.target_region,
            paper_count=len(papers_to_analyze),
            report_summary=report.summary_markdown
        )

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
