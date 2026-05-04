"""
Utility for safely converting a pandas DataFrame to a JSON-serialisable list.
"""

import math
from typing import Any
import pandas as pd

MAX_ROWS: int = 500


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a DataFrame to a list of dicts suitable for JSON serialisation.

    - Truncates to MAX_ROWS rows for AI safety.
    - Replaces NaN / Inf with None.
    - Converts datetime columns to ISO-8601 strings.

    Args:
        df: Source DataFrame.

    Returns:
        List of row dicts.
    """
    if df.empty:
        return []

    # Truncate
    df = df.head(MAX_ROWS).copy()

    # Convert datetime columns
    for col in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

    records: list[dict[str, Any]] = df.to_dict(orient="records")

    # Sanitise non-finite floats
    clean: list[dict[str, Any]] = []
    for row in records:
        clean_row: dict[str, Any] = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
            else:
                clean_row[k] = v
        clean.append(clean_row)

    return clean
