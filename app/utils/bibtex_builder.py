from typing import List
from app.models.schemas import PaperMetadata

class BibTeXBuilder:
    @staticmethod
    def generate_bibtex(papers: List[PaperMetadata]) -> str:
        """Convert list of PaperMetadata into formatted BibTeX reference strings."""
        bibtex_entries = []

        for paper in papers:
            # Generate citation key: e.g., authorLastName2024titleFirstWord
            first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
            title_word = "".join(e for e in paper.title.split()[0] if e.isalnum())
            cite_key = f"{first_author.lower()}{paper.year}{title_word.lower()}"

            authors_formatted = " and ".join(paper.authors)
            
            entry = f"""@article{{{cite_key},
  author    = {{{authors_formatted}}},
  title     = {{{{{paper.title}}}}},
  year      = {{{paper.year}}},
  journal   = {{arXiv preprint arXiv:{paper.arxiv_id if paper.arxiv_id else "N/A"}}},
  url       = {{{paper.pdf_url}}}
}}"""
            bibtex_entries.append(entry)

        return "\n\n".join(bibtex_entries)
