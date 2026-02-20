"""RSI indicator template for MT5 OHLCV data."""

from __future__ import annotations

import pandas as pd


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI).

    Args:
        close: Close price series.
        period: RSI lookback period.

    Returns:
        RSI series in range [0, 100].
    """
    if period <= 0:
        raise ValueError("period must be positive")

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    # Flat or no-loss windows should evaluate to 100.
    return rsi.fillna(100)


def add_rsi_column(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Return a copy of OHLCV DataFrame with an ``rsi`` column.

    Expects a ``close`` column in the input DataFrame.
    """
    if "close" not in df.columns:
        raise KeyError("DataFrame must contain a 'close' column")

    result = df.copy()
    result["rsi"] = calculate_rsi(result["close"], period=period)
    return result


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "close": [
                1.1000,
                1.1012,
                1.1008,
                1.1025,
                1.1030,
                1.1020,
                1.1040,
                1.1055,
                1.1048,
                1.1060,
                1.1075,
                1.1068,
                1.1080,
                1.1092,
                1.1085,
                1.1100,
            ]
        }
    )
    print(add_rsi_column(sample, period=14).tail())
