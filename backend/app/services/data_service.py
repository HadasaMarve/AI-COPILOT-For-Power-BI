"""
Data service — wraps script.get_data() and handles async-safe execution.
"""

import logging
from typing import Any
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

logger = logging.getLogger(__name__)

# Single reusable executor to avoid spawning unbounded threads
_executor = ThreadPoolExecutor(max_workers=4)


def _fetch_sync(chart_id: str, filters: dict[str, Any]) -> pd.DataFrame:
    """Synchronous wrapper around script.get_data (runs in thread pool)."""
    # Import here to avoid circular imports and allow script.py to sit at
    # the backend root without polluting the package namespace.
    import sys
    import os

    # Ensure the backend root is on the path so script.py is importable
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    from script import get_data  # type: ignore[import]

    return get_data(chart_id=chart_id, filters=filters)


async def fetch_dataframe(chart_id: str, filters: dict[str, Any]) -> pd.DataFrame:
    """
    Async-safe call to script.get_data().

    Offloads the (potentially blocking) call to a thread pool so the
    FastAPI event loop is never blocked.

    Args:
        chart_id: Visualisation identifier.
        filters:  Active filter dict.

    Returns:
        pandas DataFrame from the data source.

    Raises:
        RuntimeError: If script.get_data() raises or returns a non-DataFrame.
    """
    logger.info("Fetching data — chartId=%s filters=%s", chart_id, filters)
    loop = get_event_loop()
    try:
        df: pd.DataFrame = await loop.run_in_executor(
            _executor, _fetch_sync, chart_id, filters
        )
    except Exception as exc:
        raise RuntimeError(f"script.get_data() failed: {exc}") from exc

    if not isinstance(df, pd.DataFrame):
        raise RuntimeError("script.get_data() did not return a DataFrame.")

    logger.info("DataFrame received — rows=%d cols=%d", len(df), len(df.columns))
    return df
