import httpx
import logging
from config import settings

logger = logging.getLogger("ollama_client")

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_DEFAULT_MODEL

    async def check_health(self) -> bool:
        """Check if local Ollama server is running with ultra-fast check."""
        try:
            async with httpx.AsyncClient(timeout=0.4) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception as e:
            return False

    async def generate(self, prompt: str, system_prompt: str = None, model: str = None) -> str:
        """Send generation request to Ollama HTTP API."""
        target_model = model or self.model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
                else:
                    raise RuntimeError(f"Ollama error {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise e
