"""Execute MT5 market orders from a normalized webhook payload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import MetaTrader5 as mt5


@dataclass
class BridgeResult:
    """Result of a webhook-to-order translation and execution."""

    success: bool
    message: str
    order: Any | None = None


def execute_webhook_signal(payload: Mapping[str, Any]) -> BridgeResult:
    """Validate a webhook payload and place a market order.

    Expected payload keys:
    - symbol: str (e.g. "EURUSD")
    - side: "BUY" or "SELL"
    - volume: float lot size
    - comment: optional str
    """
    symbol = str(payload.get("symbol", "")).strip().upper()
    side = str(payload.get("side", "")).strip().upper()
    comment = str(payload.get("comment", "webhook"))

    try:
        volume = float(payload.get("volume", 0))
    except (TypeError, ValueError):
        return BridgeResult(False, "Invalid volume value")

    if not symbol or side not in {"BUY", "SELL"} or volume <= 0:
        return BridgeResult(False, "Payload must include valid symbol, side and volume")

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return BridgeResult(False, f"Symbol {symbol} not found")

    if not symbol_info.visible and not mt5.symbol_select(symbol, True):
        return BridgeResult(False, f"Unable to select symbol {symbol}")

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return BridgeResult(False, f"No tick data for {symbol}")

    order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
    price = tick.ask if side == "BUY" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        detail = result.comment if result is not None else "order_send returned None"
        return BridgeResult(False, f"Order failed: {detail}", order=result)

    return BridgeResult(True, "Order executed", order=result)
