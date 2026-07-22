"""Simple timing utilities for measuring node/agent execution latency."""
import time
from contextlib import contextmanager

from app.utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timed(label: str):
    """Context manager that logs the elapsed time of a code block."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info("TIMING | %s | %.3fs", label, elapsed)
