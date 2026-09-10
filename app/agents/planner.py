import logging
from typing import List
from app.agents.ollama_client import OllamaClient

logger = logging.getLogger("planner_agent")

class PlannerAgent:
    """Deconstructs high-level research topic into sub-queries for targeted scraping."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.ollama = ollama_client or OllamaClient()

    async def generate_subqueries(self, topic: str, count: int = 3) -> List[str]:
        """Use Ollama LLM to decompose a research topic into specific search queries."""
        system_prompt = (
            "You are an expert Computer Science research planner. "
            "Your task is to take a research topic and generate specific, high-precision academic search queries "
            "to find relevant peer-reviewed papers on ArXiv and Semantic Scholar."
        )

        user_prompt = f"""Decompose the following research topic into exactly {count} distinct academic search queries.
Topic: "{topic}"

Rules:
- Output ONLY the query strings, one per line.
- Do NOT include numbering, bullet points, or extra text.
- Focus on consensus protocols, fault tolerance, multi-agent coordination, and system resilience if applicable.

Search Queries:"""

        try:
            is_healthy = await self.ollama.check_health()
            if not is_healthy:
                logger.warning("Ollama is not responding. Falling back to default query expansion.")
                return [
                    topic,
                    f"{topic} distributed systems",
                    f"{topic} fault tolerance consensus"
                ]

            response = await self.ollama.generate(prompt=user_prompt, system_prompt=system_prompt)
            lines = [line.strip() for line in response.split("\n") if line.strip()]
            
            # Clean out any accidental numbering like "1. ", "- "
            cleaned_queries = []
            for q in lines:
                if q.startswith(tuple("123456789.-*")):
                    q = q.lstrip("0123456789.-* ").strip()
                if q:
                    cleaned_queries.append(q)

            return cleaned_queries[:count] if cleaned_queries else [topic]
        except Exception as e:
            logger.error(f"Error in PlannerAgent: {e}")
            return [topic]
