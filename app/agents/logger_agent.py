import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("logger_agent")

class LoggerAgent:
    """Manages persistent JSON work logs and session history for research queries."""

    def __init__(self, log_filepath: str = "research_log.json"):
        self.log_filepath = log_filepath

    def _load_log(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.log_filepath):
            return []
        try:
            with open(self.log_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return []

    def log_session(self, topic: str, target_region: str, paper_count: int, report_summary: str):
        """Append a new research query session entry to persistent log."""
        logs = self._load_log()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "target_region": target_region,
            "papers_analyzed": paper_count,
            "summary_snippet": report_summary[:300] + "..." if report_summary else ""
        }
        logs.append(entry)
        
        try:
            with open(self.log_filepath, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            logger.info(f"Session logged successfully to {self.log_filepath}")
        except Exception as e:
            logger.error(f"Failed to write session log: {e}")

    def log_note(self, title: str, url: str, note_text: str = ""):
        """Append an individual webpage / paper research note to persistent log."""
        logs = self._load_log()
        entry = {
            "type": "tab_note",
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "url": url,
            "note": note_text
        }
        logs.append(entry)
        try:
            with open(self.log_filepath, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            logger.info(f"Tab note logged successfully to {self.log_filepath}")
            return entry
        except Exception as e:
            logger.error(f"Failed to write note: {e}")
            return None

    def get_history(self) -> List[Dict[str, Any]]:
        return self._load_log()
