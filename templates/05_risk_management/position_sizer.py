import MetaTrader5 as mt5

def calculate_lot_size(
    symbol: str,
    risk_percent: float,
    sl_pips: float,
    account_balance: float = None
) -> float:
    """
    Calculate position size based on risk percentage.
    
    Args:
        symbol: Trading symbol
        risk_percent: Risk per trade (e.g., 1.0 for 1%)
        sl_pips: Stop loss distance in pips
        account_balance: Account balance (uses current if None)
    
    Returns:
        Recommended lot size
    """
    if account_balance is None:
        account_info = mt5.account_info()
        if account_info is None:
            # Handle case where connection or account info is missing
            return 0.0
        account_balance = account_info.balance
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.0
        
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    point = symbol_info.point
    min_lot = symbol_info.volume_min
    lot_step = symbol_info.volume_step
    max_lot = symbol_info.volume_max
    
    # Calculate pip value per lot
    # Note: tick_value is usually profit for 1 lot change by tick_size
    if tick_size == 0:
        return 0.0
        
    pip_value = (tick_value / tick_size) * point * 10
    
    # Avoid division by zero
    if sl_pips == 0 or pip_value == 0:
        return 0.0
    
    # Calculate risk amount
    risk_amount = account_balance * (risk_percent / 100)

        
    # Calculate lot size
    lot_size = risk_amount / (sl_pips * pip_value)
    
    # Round to lot step
    lot_size = max(min_lot, round(lot_size / lot_step) * lot_step)
    lot_size = min(lot_size, max_lot)
    
    return round(lot_size, 2)

if __name__ == "__main__":
    if mt5.initialize():
        # Risk 1% with 30 pip stop loss
        lot = calculate_lot_size("EURUSD", risk_percent=1.0, sl_pips=30)
        print(f"Recommended lot size: {lot}")
        
        mt5.shutdown()
    else:
        print("MT5 initialization failed")
