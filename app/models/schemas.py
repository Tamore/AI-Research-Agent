from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchQuery(BaseModel):
    topic: str = Field(..., description="Research topic or search keywords")
    target_region: Optional[str] = Field("Japan", description="Target region or country for faculty tracking")
    use_ollama: bool = Field(True, description="Whether to use local Ollama LLM")
    ollama_model: str = Field("llama3.2", description="Ollama model tag to use")
    max_papers: int = Field(5, ge=1, le=20, description="Number of papers to scrape")
    generate_ieee_pdf: bool = Field(True, description="Whether to compile an IEEE PDF draft")
    export_bibtex: bool = Field(True, description="Whether to generate BibTeX references")

class PaperMetadata(BaseModel):
    title: str
    authors: List[str]
    year: int
    published_date: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    pdf_url: str
    abstract: str
    categories: List[str] = []
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
    faculty_radar: List[FacultyProfile] = []
    bibtex_citations: str
    ieee_tex_code: Optional[str] = None
    pdf_download_url: Optional[str] = None
    analyzed_papers: List[PaperMetadata] = []
