"""Run signal checks on a fixed schedule and print actionable events."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable


def run_every(interval_seconds: int, check_fn: Callable[[], str]) -> None:
    """Execute ``check_fn`` every ``interval_seconds`` seconds."""
    print(f"Starting scheduler (interval={interval_seconds}s)")

    while True:
        started_at = datetime.now()
        signal = check_fn().upper()

        if signal != "HOLD":
            print(f"[{started_at:%Y-%m-%d %H:%M:%S}] Signal detected: {signal}")

        elapsed = (datetime.now() - started_at).total_seconds()
        sleep_for = max(interval_seconds - elapsed, 0)
        time.sleep(sleep_for)


def simple_price_action_signal(symbol: str = "EURUSD") -> str:
    """Example signal source using the latest two H1 candles."""
    import MetaTrader5 as mt5

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 2)
    if rates is None or len(rates) < 2:
        return "HOLD"

    prev_close = rates[0]["close"]
    last_close = rates[1]["close"]

    if last_close > prev_close:
        return "BUY"
    if last_close < prev_close:
        return "SELL"
    return "HOLD"


if __name__ == "__main__":
    import MetaTrader5 as mt5

    if not mt5.initialize():
        raise SystemExit(f"MT5 init failed: {mt5.last_error()}")

    try:
        run_every(interval_seconds=300, check_fn=lambda: simple_price_action_signal("EURUSD"))
    finally:
        mt5.shutdown()
