import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("logger_agent")

class LoggerAgent:
    """Manages persistent JSON work logs, folder-organized research notes, and paper history."""

    def __init__(self, log_filepath: str = "research_log.json", papers_filepath: str = "generated_papers.json"):
        self.log_filepath = log_filepath
        self.papers_filepath = papers_filepath

    def _load_json(self, filepath: str) -> List[Dict[str, Any]]:
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []

    def _save_json(self, filepath: str, data: List[Dict[str, Any]]):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to write {filepath}: {e}")

    def log_session(self, topic: str, target_region: str, paper_count: int, report_summary: str, pdf_path: str = ""):
        """Append a session entry and record in generated papers library."""
        logs = self._load_json(self.log_filepath)
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "research_session",
            "timestamp": timestamp,
            "topic": topic,
            "target_region": target_region,
            "papers_analyzed": paper_count,
            "summary_snippet": report_summary[:300] + "..." if report_summary else "",
            "pdf_url": f"/api/v1/download-pdf?filepath={pdf_path}" if pdf_path else ""
        }
        logs.append(entry)
        self._save_json(self.log_filepath, logs)

        if pdf_path and os.path.exists(pdf_path):
            papers = self._load_json(self.papers_filepath)
            paper_entry = {
                "id": f"paper_{int(datetime.now().timestamp())}",
                "timestamp": timestamp,
                "title": topic,
                "target_region": target_region,
                "pdf_filename": pdf_path,
                "download_url": f"/api/v1/download-pdf?filepath={pdf_path}",
                "summary": report_summary[:250] if report_summary else ""
            }
            papers.insert(0, paper_entry)
            self._save_json(self.papers_filepath, papers)

    def log_note(self, title: str, url: str, note_text: str = "", folder: str = "General Research"):
        """Save a research note categorized by topic folder."""
        logs = self._load_json(self.log_filepath)
        entry = {
            "type": "tab_note",
            "timestamp": datetime.now().isoformat(),
            "folder": folder or "General Research",
            "title": title,
            "url": url,
            "note": note_text
        }
        logs.append(entry)
        self._save_json(self.log_filepath, logs)
        return entry

    def get_notes_by_folder(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group all saved research notes by folder."""
        logs = self._load_json(self.log_filepath)
        folders: Dict[str, List[Dict[str, Any]]] = {
            "General Research": [],
            "Event-Driven & AI Agents": [],
            "Japan Universities Plan B": []
        }
        for item in logs:
            if item.get("type") == "tab_note":
                f = item.get("folder") or "General Research"
                if f not in folders:
                    folders[f] = []
                folders[f].insert(0, item)
        return folders

    def get_generated_papers(self) -> List[Dict[str, Any]]:
        """Retrieve list of all compiled IEEE drafts and research reports."""
        return self._load_json(self.papers_filepath)

    def get_history(self) -> List[Dict[str, Any]]:
        return self._load_json(self.log_filepath)
