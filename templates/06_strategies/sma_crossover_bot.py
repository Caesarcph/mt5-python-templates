"""SMA crossover strategy template for MT5.

- BUY when fast SMA crosses above slow SMA
- SELL when fast SMA crosses below slow SMA
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import MetaTrader5 as mt5
import pandas as pd


@dataclass
class CrossoverSignal:
    action: str  # BUY | SELL | HOLD
    price: float


class SMACrossoverBot:
    def __init__(
        self,
        symbol: str = "EURUSD",
        timeframe: int = mt5.TIMEFRAME_M15,
        fast_period: int = 10,
        slow_period: int = 30,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.fast_period = fast_period
        self.slow_period = slow_period

    def get_signal(self) -> CrossoverSignal:
        bars = max(self.fast_period, self.slow_period) + 5
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None or len(rates) < bars:
            return CrossoverSignal("HOLD", 0.0)

        frame = pd.DataFrame(rates)
        frame["fast"] = frame["close"].rolling(self.fast_period).mean()
        frame["slow"] = frame["close"].rolling(self.slow_period).mean()

        prev_fast = frame["fast"].iloc[-2]
        prev_slow = frame["slow"].iloc[-2]
        curr_fast = frame["fast"].iloc[-1]
        curr_slow = frame["slow"].iloc[-1]
        price = float(frame["close"].iloc[-1])

        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return CrossoverSignal("BUY", price)
        if prev_fast >= prev_slow and curr_fast < curr_slow:
            return CrossoverSignal("SELL", price)
        return CrossoverSignal("HOLD", price)

    def run(self, poll_seconds: int = 60) -> None:
        print(f"Running SMA crossover on {self.symbol}")
        while True:
            signal = self.get_signal()
            if signal.action != "HOLD":
                print(f"Signal={signal.action} price={signal.price:.5f}")
            time.sleep(poll_seconds)


if __name__ == "__main__":
    if not mt5.initialize():
        print(f"MT5 init failed: {mt5.last_error()}")
    else:
        try:
            SMACrossoverBot().run()
        finally:
            mt5.shutdown()
