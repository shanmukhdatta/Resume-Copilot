"""Optional OpenAI provider implementation (kept behind the LLM factory
so it can be swapped in without touching agent code)."""
from app.config import get_settings
from app.llm.retry import async_retry
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self._client = None
        if self.api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not installed; running in stub mode.")

    @async_retry(max_retries=2)
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self._client is None:
            return "{}"
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt or ""},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
