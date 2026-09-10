import arxiv
import logging
from typing import List
from app.models.schemas import PaperMetadata

logger = logging.getLogger("arxiv_client")

class ArXivClient:
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.client = arxiv.Client()

    def search_papers(self, query: str, max_results: int = None) -> List[PaperMetadata]:
        """Search ArXiv API for papers matching query."""
        limit = max_results or self.max_results
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers: List[PaperMetadata] = []
        try:
            results = list(self.client.results(search))
            for paper in results:
                authors = [author.name for author in paper.authors]
                published_date = paper.published.strftime("%Y-%m-%d")
                year = paper.published.year

                papers.append(
                    PaperMetadata(
                        title=paper.title.strip(),
                        authors=authors,
                        year=year,
                        published_date=published_date,
                        arxiv_id=paper.entry_id.split('/')[-1],
                        doi=paper.doi,
                        pdf_url=paper.pdf_url,
                        abstract=paper.summary.strip().replace('\n', ' '),
                        categories=paper.categories
                    )
                )
        except Exception as e:
            logger.error(f"Error querying ArXiv API: {e}")
            raise e

        return papers
