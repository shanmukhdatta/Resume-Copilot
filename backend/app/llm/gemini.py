"""Gemini provider implementation of the BaseLLMClient interface."""
from app.config import get_settings
from app.llm.retry import async_retry
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Thin async wrapper around the google-generativeai SDK."""

    def __init__(self):
        settings = get_settings()
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.api_key = settings.GEMINI_API_KEY
        self._model = None

        if self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except ImportError:
                logger.warning(
                    "google-generativeai not installed; GeminiClient running in "
                    "stub mode."
                )
        else:
            logger.warning("GEMINI_API_KEY not set; GeminiClient running in stub mode.")

    @async_retry(max_retries=2)
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate raw text output from Gemini for the given prompt."""
        if self._model is None:
            return self._stub_response(prompt)

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        import asyncio

        def _call():
            response = self._model.generate_content(
                full_prompt,
                generation_config={"temperature": self.temperature},
            )
            return response.text

        return await asyncio.to_thread(_call)

    @staticmethod
    def _stub_response(prompt: str) -> str:
        """Deterministic offline fallback so the pipeline is runnable and
        testable without a live API key."""
        logger.info("Using stub LLM response (no API key configured).")
        return "{}"
