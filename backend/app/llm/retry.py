"""Async retry decorator used for resilient LLM calls."""
import asyncio
import functools

from app.utils.logger import get_logger

logger = get_logger(__name__)


def async_retry(max_retries: int = 2, base_delay: float = 1.0):
    """Retry an async function with exponential backoff on failure."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    if attempt < max_retries:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            "Retry %s/%s for %s after error: %s (sleeping %.1fs)",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            exc,
                            delay,
                        )
                        await asyncio.sleep(delay)
            raise last_exc

        return wrapper

    return decorator
