import MetaTrader5 as mt5
from typing import Dict, List, Any


def get_open_positions_summary(symbol: str | None = None) -> List[Dict[str, Any]]:
    """Return normalized summary for open MT5 positions.

    Args:
        symbol: Optional symbol filter (e.g. "EURUSD").

    Returns:
        A list of dicts with key fields for monitoring positions.
    """
    positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    if positions is None:
        return []

    summary: List[Dict[str, Any]] = []
    for pos in positions:
        summary.append(
            {
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "type": "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL",
                "volume": pos.volume,
                "open_price": pos.price_open,
                "current_price": pos.price_current,
                "profit": pos.profit,
                "swap": pos.swap,
                "comment": pos.comment,
            }
        )

    return summary


if __name__ == "__main__":
    if not mt5.initialize():
        print("MT5 initialization failed")
    else:
        rows = get_open_positions_summary()
        if not rows:
            print("No open positions")
        else:
            for row in rows:
                print(row)
        mt5.shutdown()
