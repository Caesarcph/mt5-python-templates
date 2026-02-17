#!/usr/bin/env python3
"""
Order Management Template for MetaTrader 5
Handles market orders and closing positions with basic error checking.
"""

import MetaTrader5 as mt5
from dataclasses import dataclass
from typing import Literal, Optional, Tuple

@dataclass
class TradeResult:
    success: bool
    ticket: int = 0
    price: float = 0.0
    message: str = ""


def _calculate_sl_tp(
    direction: Literal["BUY", "SELL"],
    price: float,
    point: float,
    sl_pips: Optional[float],
    tp_pips: Optional[float],
) -> Tuple[float, float]:
    """Calculate SL/TP prices based on order direction."""
    pip_value = point * 10

    if direction == "BUY":
        sl = price - sl_pips * pip_value if sl_pips else 0.0
        tp = price + tp_pips * pip_value if tp_pips else 0.0
    else:
        sl = price + sl_pips * pip_value if sl_pips else 0.0
        tp = price - tp_pips * pip_value if tp_pips else 0.0

    return sl, tp


def market_order(
    symbol: str,
    order_type: Literal["BUY", "SELL"],
    volume: float,
    sl_pips: Optional[float] = None,
    tp_pips: Optional[float] = None,
    comment: str = "",
    magic: int = 0
) -> TradeResult:
    """
    Execute a market order with optional SL/TP.
    
    Args:
        symbol: Trading symbol
        order_type: "BUY" or "SELL"
        volume: Lot size
        sl_pips: Stop loss in pips (optional)
        tp_pips: Take profit in pips (optional)
        comment: Order comment
        magic: Magic number for EA identification
    
    Returns:
        TradeResult with execution details
    """
    # Check symbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return TradeResult(False, message=f"Symbol {symbol} not found")
    
    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
             return TradeResult(False, message=f"Symbol {symbol} not visible and selection failed")
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return TradeResult(False, message=f"Failed to get tick for {symbol}")
        
    point = symbol_info.point
    
    # Determine order type and price
    normalized_type = order_type.upper()
    if normalized_type == "BUY":
        mt5_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    elif normalized_type == "SELL":
        mt5_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    else:
        return TradeResult(False, message=f"Invalid order type: {order_type}")

    sl, tp = _calculate_sl_tp(normalized_type, price, point, sl_pips, tp_pips)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    
    if result is None:
         return TradeResult(False, message="Order send failed (result is None)")
         
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return TradeResult(
            False, 
            message=f"Order failed: {result.comment} (code: {result.retcode})"
        )
    
    return TradeResult(
        True,
        ticket=result.order,
        price=result.price,
        message=f"Order executed at {result.price}"
    )

def close_position(ticket: int, comment: str = "") -> TradeResult:
    """Close a position by ticket number."""
    # Retrieve position
    positions = mt5.positions_get(ticket=ticket)
    if not positions:
        return TradeResult(False, message=f"Position {ticket} not found")
    
    pos = positions[0]
    
    # Reverse the position type to close it
    # 0 = BUY, 1 = SELL
    close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
    
    # Get current price
    tick = mt5.symbol_info_tick(pos.symbol)
    if tick is None:
        return TradeResult(False, message=f"Tick not available for {pos.symbol}")
        
    price = tick.bid if pos.type == 0 else tick.ask
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "type": close_type,
        "position": ticket,
        "price": price,
        "deviation": 20,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    
    if result is None:
        return TradeResult(False, message="Order send failed (result is None)")
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return TradeResult(False, message=f"Close failed: {result.comment}")
    
    return TradeResult(True, price=result.price, message="Position closed")

# Usage
if __name__ == "__main__":
    if mt5.initialize():
        print("MT5 Initialized")
        
        # Example: Open a buy position (Demo only! check your account)
        # result = market_order("EURUSD", "BUY", 0.01, sl_pips=50, tp_pips=100)
        # print(result)
        
        mt5.shutdown()
    else:
        print("MT5 Initialization failed")
