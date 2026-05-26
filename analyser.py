"""
analyser.py
-----------
Core exception analysis engine.
Runs three checks on every numeric column in the uploaded CSV:
  1. Null / missing values
  2. Z-score outliers  (|z| > 3  → statistically extreme)
  3. IQR range check   (below Q1-1.5*IQR or above Q3+1.5*IQR → likely anomaly)

Returns a list of flagged rows with a risk_score (0-100) and human-readable reason.
This mirrors the exception-identification logic Om used at KPMG with SQL + Excel,
now expressed as a reusable Python module.
"""

import pandas as pd
import numpy as np
from typing import Any


def _zscore(series: pd.Series) -> pd.Series:
    """Return z-scores for a numeric series (NaN-safe)."""
    mean = series.mean()
    std  = series.std()
    if std == 0:
        return pd.Series(0.0, index=series.index)
    return (series - mean) / std


def _iqr_bounds(series: pd.Series) -> tuple[float, float]:
    """Return (lower, upper) IQR fences for a numeric series."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def analyse(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Run exception analysis on a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw audit evidence loaded from the uploaded CSV.

    Returns
    -------
    List of dicts, one per flagged row, sorted by risk_score descending.
    Each dict contains:
        row_index    : original CSV row number
        risk_score   : 0-100 (higher = riskier)
        flags        : list of flag strings
        row_data     : original row as a dict
    """
    flagged: list[dict[str, Any]] = []

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Pre-compute z-scores and IQR bounds for every numeric column
    zscores: dict[str, pd.Series] = {}
    iqr_bounds_map: dict[str, tuple[float, float]] = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 3:          # not enough data for meaningful stats
            continue
        zscores[col]       = _zscore(df[col])
        iqr_bounds_map[col] = _iqr_bounds(series)

    for idx, row in df.iterrows():
        flags: list[str] = []
        score = 0

        # --- Check 1: Null / missing values ---
        null_cols = [c for c in df.columns if pd.isnull(row[c])]
        if null_cols:
            flags.append(f"Missing values in: {', '.join(null_cols)}")
            score += 20 * len(null_cols)          # 20 pts per missing field

        # --- Check 2 & 3: Numeric anomalies ---
        for col in numeric_cols:
            if col not in zscores:
                continue
            val = row[col]
            if pd.isnull(val):
                continue                           # already caught above

            z = abs(zscores[col].get(idx, 0))
            lo, hi = iqr_bounds_map[col]

            if z > 3:
                flags.append(
                    f"'{col}' = {val:.2f} is a statistical outlier (|z| = {z:.1f})"
                )
                score += min(30, int(z * 8))       # caps at 30 pts per column

            elif val < lo or val > hi:
                direction = "below lower" if val < lo else "above upper"
                flags.append(
                    f"'{col}' = {val:.2f} is {direction} IQR fence ({lo:.2f}, {hi:.2f})"
                )
                score += 15

        if flags:
            flagged.append(
                {
                    "row_index":  int(idx) + 2,    # +2 = 1-based + header row
                    "risk_score": min(score, 100),  # cap at 100
                    "flags":      flags,
                    "row_data":   row.where(pd.notnull(row), None).to_dict(),
                }
            )

    # Sort highest risk first
    flagged.sort(key=lambda x: x["risk_score"], reverse=True)
    return flagged
