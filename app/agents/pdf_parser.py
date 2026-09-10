import os
import httpx
import pdfplumber
import io
import logging
from typing import Dict, Any

logger = logging.getLogger("pdf_parser")

class PDFParser:
    """Downloader and extractor for academic paper PDFs."""

    @staticmethod
    async def download_pdf_bytes(pdf_url: str) -> bytes:
        """Asynchronously download PDF bytes from URL."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                res = await client.get(pdf_url, headers=headers)
                if res.status_code == 200:
                    return res.content
                else:
                    logger.error(f"Failed to download PDF from {pdf_url}, status: {res.status_code}")
                    return b""
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return b""

    @classmethod
    async def extract_sections(cls, pdf_url: str, max_pages: int = 6) -> Dict[str, Any]:
        """Download PDF and parse key sections: Abstract, Methodology, Results/Evaluation."""
        pdf_bytes = await cls.download_pdf_bytes(pdf_url)
        if not pdf_bytes:
            return {"full_text": "", "extracted": False}

        full_text = ""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Read up to max_pages
                for page_idx in range(min(len(pdf.pages), max_pages)):
                    page_text = pdf.pages[page_idx].extract_text()
                    if page_text:
                        full_text += page_text + "\n\n"
        except Exception as e:
            logger.error(f"Error parsing PDF with pdfplumber: {e}")
            return {"full_text": "", "extracted": False}

        return {
            "full_text": full_text.strip(),
            "page_count": len(pdf.pages) if 'pdf' in locals() else 0,
            "extracted": True
        }
