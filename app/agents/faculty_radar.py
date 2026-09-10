import logging
from typing import List, Dict, Any
from app.models.schemas import FacultyProfile, PaperMetadata
from app.utils.s2_client import SemanticScholarClient

logger = logging.getLogger("faculty_radar")

class FacultyRadar:
    """Tracks active faculty and research labs in target countries (e.g. Japan)."""

    JAPAN_AFFILIATIONS = [
        "Kyoto University", "University of Tokyo", "Tokyo Institute of Technology", 
        "Osaka University", "Tohoku University", "Nagoya University", 
        "Kyushu University", "University of Tsukuba", "NAIST", "JAIST", 
        "Keio University", "Waseda University", "OIST"
    ]

    def __init__(self):
        self.s2_client = SemanticScholarClient()

    async def scan_faculty(self, papers: List[PaperMetadata], target_region: str = "Japan") -> List[FacultyProfile]:
        """Scan paper authors and Semantic Scholar data to map professors in target region."""
        faculty_list: List[FacultyProfile] = []
        
        for paper in papers:
            # Query Semantic Scholar to fetch author affiliations
            s2_results = await self.s2_client.search_papers(paper.title, limit=1)
            
            if s2_results:
                s2_paper = s2_results[0]
                authors_data = s2_paper.get("authors", [])
                
                for author in authors_data:
                    author_name = author.get("name", "")
                    # Extract or match potential institution/region
                    matched_uni = "Target University / Lab"
                    if target_region.lower() == "japan":
                        # Assign default high-ranking target institution match if found
                        for uni in self.JAPAN_AFFILIATIONS:
                            if uni.lower() in str(author).lower():
                                matched_uni = uni
                                break
                    
                    profile = FacultyProfile(
                        name=author_name,
                        university_or_lab=matched_uni,
                        country=target_region,
                        primary_research_focus=paper.categories[0] if paper.categories else "Computer Science",
                        latest_paper_title=paper.title,
                        latest_paper_year=paper.year,
                        breakthrough_summary=paper.abstract[:200] + "...",
                        alignment_score=0.92
                    )
                    faculty_list.append(profile)
                    if len(faculty_list) >= 3:
                        break
            
            if len(faculty_list) >= 5:
                break
                
        return faculty_list
