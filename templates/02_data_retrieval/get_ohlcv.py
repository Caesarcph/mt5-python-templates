#!/usr/bin/env python3
"""
Data Retrieval Template for MetaTrader 5
Retrieves OHLCV history and real-time tick data.
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Union

def get_ohlcv(
    symbol: str,
    timeframe: int = mt5.TIMEFRAME_H1,
    bars: int = 1000,
    start_time: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Get OHLCV data as a pandas DataFrame.
    
    Args:
        symbol: Trading symbol (e.g., "EURUSD")
        timeframe: MT5 timeframe constant (default: H1)
        bars: Number of bars to retrieve
        start_time: Start from specific time (default: now)
    
    Returns:
        DataFrame with columns: time (index), open, high, low, close, tick_volume
    """
    if start_time is None:
        start_time = datetime.now()
    
    # Retrieve rates from MT5
    rates = mt5.copy_rates_from(symbol, timeframe, start_time, bars)
    
    if rates is None or len(rates) == 0:
        error_code = mt5.last_error()
        print(f"Failed to get rates for {symbol}. Error: {error_code}")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    
    # Convert timestamp to datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Set time as index
    df.set_index('time', inplace=True)
    
    # Return standard columns
    return df[['open', 'high', 'low', 'close', 'tick_volume']]

def get_latest_tick(symbol: str) -> Optional[Dict[str, Union[datetime, float, int]]]:
    """
    Get the most recent tick for a symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Dictionary with tick data or None if failed
    """
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        return None
        
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick for {symbol}")
        return None
    
    return {
        'time': datetime.fromtimestamp(tick.time),
        'bid': tick.bid,
        'ask': tick.ask,
        'spread': round((tick.ask - tick.bid) * 10000, 1),  # Estimate in pips (for standard pairs)
        'volume': tick.volume,
        'flags': tick.flags
    }

# Usage Example
if __name__ == "__main__":
    # Initialize connection (update path/login if needed, or rely on auto-find)
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    else:
        print("MT5 Initialized")
        
        # Example 1: Get History
        symbol = "EURUSD"
        print(f"\nFetching {symbol} H1 data...")
        df = get_ohlcv(symbol, mt5.TIMEFRAME_H1, 10)
        if not df.empty:
            print(df)
        else:
            print("No data received.")
            
        # Example 2: Get Live Tick
        print(f"\nFetching {symbol} tick...")
        tick = get_latest_tick(symbol)
        if tick:
            print(f"Tick: {tick}")
            
        mt5.shutdown()
