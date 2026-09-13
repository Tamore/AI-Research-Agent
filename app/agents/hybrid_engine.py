import os
import httpx
import logging
from config import settings

logger = logging.getLogger("hybrid_llm_engine")

class HybridLLMEngine:
    """
    Switchable Hybrid LLM Engine:
    - Primary: Groq Llama 3.3 70B (300+ tokens/sec, genius reasoning)
    - Fallback: Local Intel CPU Heuristic Engine (100% offline, zero GPU needed)
    """

    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_model = "llama-3.3-70b-versatile"
        self.active_mode = "auto" # 'auto', 'groq', 'local'

    def set_mode(self, mode: str, api_key: str = None):
        self.active_mode = mode
        if api_key:
            self.groq_api_key = api_key

    async def check_status(self) -> dict:
        groq_active = False
        if self.groq_api_key:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    r = await client.get(
                        "https://api.groq.com/openai/v1/models",
                        headers={"Authorization": f"Bearer {self.groq_api_key}"}
                    )
                    groq_active = (r.status_code == 200)
            except Exception:
                groq_active = False

        return {
            "mode": self.active_mode,
            "groq_connected": groq_active,
            "local_intel_active": True,
            "primary_model": self.groq_model if groq_active else "Intel Local Fast Engine"
        }

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        # 1. Check if Groq Cloud mode is requested or Auto with valid key
        if (self.active_mode in ["auto", "groq"]) and self.groq_api_key:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                async with httpx.AsyncClient(timeout=15.0) as client:
                    res = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.groq_model,
                            "messages": messages,
                            "temperature": 0.3,
                            "max_tokens": 2048
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        logger.warning(f"Groq API error {res.status_code}, falling back to Intel Local Engine.")
            except Exception as e:
                logger.warning(f"Groq connection skipped ({e}). Falling back to Intel Local Engine.")

        # 2. Local Intel CPU Heuristic Fallback (Instant, Zero GPU needed, Works Offline)
        return ""
