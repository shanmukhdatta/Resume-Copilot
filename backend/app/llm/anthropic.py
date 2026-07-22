"""Optional Anthropic provider implementation (kept behind the LLM
factory so it can be swapped in without touching agent code)."""
from app.config import get_settings
from app.llm.retry import async_retry
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AnthropicClient:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ANTHROPIC_API_KEY
        self._client = None
        if self.api_key:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.warning("anthropic package not installed; running in stub mode.")

    @async_retry(max_retries=2)
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self._client is None:
            return "{}"
        response = await self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
