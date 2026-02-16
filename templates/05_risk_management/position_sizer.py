"""Position sizing helpers for MT5 risk-based lot calculation."""

from typing import Optional

import MetaTrader5 as mt5


def _normalize_lot_size(raw_lot: float, min_lot: float, max_lot: float, lot_step: float) -> float:
    """Normalize lot size to broker constraints."""
    if lot_step <= 0:
        return 0.0

    normalized = round(raw_lot / lot_step) * lot_step
    normalized = max(min_lot, min(normalized, max_lot))
    return round(normalized, 2)


def calculate_lot_size(
    symbol: str,
    risk_percent: float,
    sl_pips: float,
    account_balance: Optional[float] = None,
) -> float:
    """Calculate lot size from account risk percentage.

    Args:
        symbol: Trading symbol (e.g. "EURUSD").
        risk_percent: Risk per trade in percent (1.0 means 1%).
        sl_pips: Stop-loss distance in pips.
        account_balance: Optional account balance override.

    Returns:
        Recommended lot size. Returns 0.0 when required MT5 values are unavailable.
    """
    if risk_percent <= 0 or sl_pips <= 0:
        return 0.0

    if account_balance is None:
        account_info = mt5.account_info()
        if account_info is None:
            return 0.0
        account_balance = account_info.balance

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.0

    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    point = symbol_info.point

    if tick_size <= 0 or point <= 0:
        return 0.0

    # tick_value is profit/loss change per tick movement for 1 lot.
    pip_value = (tick_value / tick_size) * point * 10
    if pip_value <= 0:
        return 0.0

    risk_amount = account_balance * (risk_percent / 100)
    raw_lot = risk_amount / (sl_pips * pip_value)

    return _normalize_lot_size(
        raw_lot=raw_lot,
        min_lot=symbol_info.volume_min,
        max_lot=symbol_info.volume_max,
        lot_step=symbol_info.volume_step,
    )


if __name__ == "__main__":
    if mt5.initialize():
        lot = calculate_lot_size("EURUSD", risk_percent=1.0, sl_pips=30)
        print(f"Recommended lot size: {lot}")
        mt5.shutdown()
    else:
        print("MT5 initialization failed")
