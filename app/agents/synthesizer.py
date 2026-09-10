import logging
from typing import List, Dict, Any
from app.models.schemas import PaperMetadata, ResearchReport, FacultyProfile
from app.agents.ollama_client import OllamaClient
from app.utils.bibtex_builder import BibTeXBuilder

logger = logging.getLogger("synthesizer_agent")

class SynthesizerAgent:
    """Core synthesis engine generating Markdown literature reviews, comparison matrices, and citations."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.ollama = ollama_client or OllamaClient()

    async def generate_report(
        self, 
        topic: str, 
        papers: List[PaperMetadata], 
        faculty: List[FacultyProfile] = [], 
        target_region: str = "Japan"
    ) -> ResearchReport:
        """Synthesize parsed paper data into a full structured research report."""

        # 1. Build Literature Matrix
        matrix_md = self._build_literature_matrix(papers)

        # 2. Build BibTeX References
        bibtex_code = BibTeXBuilder.generate_bibtex(papers)

        # 3. Generate Executive Summary & Synthesis via Ollama
        system_prompt = (
            "You are a Senior Academic Researcher and Computer Science Professor. "
            "Synthesize paper abstracts and methodologies into a clear, rigorous, academic literature review."
        )

        paper_summaries_text = "\n\n".join([
            f"Paper [{i+1}]: {p.title} ({p.year})\nAuthors: {', '.join(p.authors)}\nAbstract: {p.abstract}"
            for i, p in enumerate(papers)
        ])

        user_prompt = f"""Write an academic literature review report on the topic: "{topic}".

Base your analysis on these analyzed papers:
{paper_summaries_text}

Requirements:
- Structure the synthesis with headings: ## Executive Summary, ## Key Methodologies & Architectural Trade-Offs, and ## Future Research Directions.
- Use inline citation markers like [1], [2] corresponding to the paper numbers provided above.
- Be concise, formal, and precise.

Literature Review:"""

        try:
            is_healthy = await self.ollama.check_health()
            if is_healthy:
                summary_md = await self.ollama.generate(prompt=user_prompt, system_prompt=system_prompt)
            else:
                summary_md = self._fallback_summary(topic, papers)
        except Exception as e:
            logger.error(f"Error in SynthesizerAgent: {e}")
            summary_md = self._fallback_summary(topic, papers)

        return ResearchReport(
            topic=topic,
            target_region=target_region,
            summary_markdown=summary_md,
            literature_matrix=matrix_md,
            faculty_radar=faculty,
            bibtex_citations=bibtex_code,
            analyzed_papers=papers
        )

    def _build_literature_matrix(self, papers: List[PaperMetadata]) -> str:
        """Generate GitHub Flavored Markdown comparison table across analyzed papers."""
        headers = "| # | Paper Title | Year | Core Methodology / Focus | Categories |"
        divider = "| :-: | :--- | :-: | :--- | :--- |"
        rows = []

        for idx, p in enumerate(papers, start=1):
            title = p.title.replace("|", "-")
            methodology = p.abstract[:120].replace("\n", " ").replace("|", "-") + "..."
            cats = ", ".join(p.categories[:2]) if p.categories else "CS"
            rows.append(f"| [{idx}] | **{title}** | {p.year} | {methodology} | {cats} |")

        return "\n".join([headers, divider] + rows)

    def _fallback_summary(self, topic: str, papers: List[PaperMetadata]) -> str:
        """Fallback markdown summary when Ollama LLM is offline."""
        lines = [
            f"## Executive Summary: {topic}\n",
            f"This synthesized literature report analyzes {len(papers)} peer-reviewed computer science publications.\n",
            "### Analyzed Publications:"
        ]
        for idx, p in enumerate(papers, start=1):
            lines.append(f"{idx}. **{p.title}** ({p.year}) - *{', '.join(p.authors[:3])}*")
        return "\n".join(lines)
