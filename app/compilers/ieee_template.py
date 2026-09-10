from typing import List
from app.models.schemas import PaperMetadata, ResearchReport

class IEEETemplateBuilder:
    """Generates standard IEEE two-column LaTeX source code (.tex)."""

    @staticmethod
    def build_tex(report: ResearchReport) -> str:
        authors_formatted = "Nirmiti R. Tamore"
        
        abstract_text = (
            f"This paper presents a synthesized literature review on {report.topic}. "
            f"We analyze {len(report.analyzed_papers)} state-of-the-art peer-reviewed publications, "
            f"evaluating core consensus methodologies, fault-tolerance paradigms, and system resilience."
        )

        paper_sections = ""
        for idx, paper in enumerate(report.analyzed_papers, start=1):
            paper_sections += f"""
\\subsection{{Analysis of {paper.title[:50]}...}}
\\textbf{{Authors:}} {", ".join(paper.authors[:3])} ({paper.year})\\\\
\\textbf{{Abstract Summary:}} {paper.abstract[:350]}...

"""

        tex_code = f"""\\documentclass[conference]{{IEEEtran}}
\\usepackage{{cite}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{algorithmic}}
\\usepackage{{graphicx}}
\\usepackage{{textcomp}}
\\usepackage{{xcolor}}

\\begin{{document}}

\\title{{{report.topic}: An Academic Literature Review and Comparative Analysis}}

\\author{{\\IEEEauthorblockN{{{authors_formatted}}}
\\IEEEauthorblockA{{\\textit{{Computer Science & Engineering}} \\\\
\\textit{{Research Agent Synthesized Draft}}\\\\
Pune, India\\\\
tamorenirmiti@gmail.com}}
}}

\\maketitle

\\begin{{abstract}}
{abstract_text}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
Distributed Systems, Fault Tolerance, Multi-Agent Systems, Consensus Protocols, Literature Review
\\end{{IEEEkeywords}}

\\section{{Introduction}}
The rapid proliferation of distributed systems and autonomous agent networks necessitates robust coordination protocols. This document compiles a comparative evaluation of recent academic literature addressing state synchronization, leader election, and failure recovery.

\\section{{Synthesized Literature Survey}}
{report.summary_markdown.replace('#', '')}

\\section{{Comparative Methodology Analysis}}
{paper_sections}

\\section{{BibTeX References}}
{report.bibtex_citations}

\\end{{document}}
"""
        return tex_code
