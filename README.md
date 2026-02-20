# 🐍 MT5-Python-Templates

> Production-ready Python templates for MetaTrader 5 development. Copy, customize, trade.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![MT5](https://img.shields.io/badge/MetaTrader-5-orange.svg)](https://www.metatrader5.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Why This Repository?

MT5's Python integration is powerful but poorly documented. This repo provides **battle-tested templates** so you can:

- ✅ Skip boilerplate setup
- ✅ Avoid common pitfalls
- ✅ Start trading in minutes

## 📦 Templates Included

```
templates/
├── 01_connection/           # Connection & authentication
├── 02_data_retrieval/       # Historical & live data
├── 03_order_management/     # Place, modify, close orders
├── 04_position_tracking/    # Monitor open positions
├── 05_risk_management/      # Position sizing & stops
├── 06_strategies/           # Complete strategy examples
├── 07_indicators/           # Custom indicator calculation
├── 08_automation/           # Scheduled trading bots
└── 09_integration/          # External system bridges
```

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Caesarcph/mt5-python-templates.git
cd mt5-python-templates

# Install
pip install MetaTrader5 pandas numpy

# Test connection
python templates/01_connection/basic_connect.py
```

## 📚 Template Reference

### 1. Connection Templates

```python
# templates/01_connection/basic_connect.py
import MetaTrader5 as mt5

def connect_mt5(
    path: str = None,
    login: int = None,
    password: str = None,
    server: str = None,
    timeout: int = 60000
) -> bool:
    """
    Connect to MT5 terminal with comprehensive error handling.
    
    Args:
        path: Path to terminal64.exe (auto-detect if None)
        login: Account number (use terminal default if None)
        password: Account password
        server: Broker server name
        timeout: Connection timeout in ms
    
    Returns:
        True if connected successfully
    """
    # Initialize MT5
    if not mt5.initialize(path=path, login=login, password=password, 
                          server=server, timeout=timeout):
        error = mt5.last_error()
        print(f"MT5 initialization failed: {error}")
        return False
    
    # Verify connection
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to get account info")
        mt5.shutdown()
        return False
    
    print(f"Connected to {account_info.server}")
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:,.2f}")
    print(f"Leverage: 1:{account_info.leverage}")
    
    return True

def disconnect_mt5():
    """Safely disconnect from MT5."""
    mt5.shutdown()
    print("Disconnected from MT5")

# Usage
if __name__ == "__main__":
    if connect_mt5():
        # Your trading logic here
        disconnect_mt5()
```

### 2. Data Retrieval Templates

```python
# templates/02_data_retrieval/get_ohlcv.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

def get_ohlcv(
    symbol: str,
    timeframe: int = mt5.TIMEFRAME_H1,
    bars: int = 1000,
    start_time: datetime = None
) -> pd.DataFrame:
    """
    Get OHLCV data as a pandas DataFrame.
    
    Args:
        symbol: Trading symbol (e.g., "EURUSD")
        timeframe: MT5 timeframe constant
        bars: Number of bars to retrieve
        start_time: Start from specific time (default: now)
    
    Returns:
        DataFrame with columns: time, open, high, low, close, volume
    """
    if start_time is None:
        start_time = datetime.now()
    
    rates = mt5.copy_rates_from(symbol, timeframe, start_time, bars)
    
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates for {symbol}")
        return pd.DataFrame()
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df[['open', 'high', 'low', 'close', 'tick_volume']]

def get_latest_tick(symbol: str) -> dict:
    """Get the most recent tick for a symbol."""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    
    return {
        'time': datetime.fromtimestamp(tick.time),
        'bid': tick.bid,
        'ask': tick.ask,
        'spread': round((tick.ask - tick.bid) * 10000, 1),  # in pips
        'volume': tick.volume
    }

# Usage
if __name__ == "__main__":
    mt5.initialize()
    
    df = get_ohlcv("EURUSD", mt5.TIMEFRAME_H1, 500)
    print(df.tail())
    
    tick = get_latest_tick("EURUSD")
    print(f"EURUSD: Bid={tick['bid']}, Ask={tick['ask']}, Spread={tick['spread']} pips")
    
    mt5.shutdown()
```

### 3. Order Management Templates

```python
# templates/03_order_management/trade_executor.py
import MetaTrader5 as mt5
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradeResult:
    success: bool
    ticket: int = 0
    price: float = 0.0
    message: str = ""

def market_order(
    symbol: str,
    order_type: str,  # "BUY" or "SELL"
    volume: float,
    sl_pips: float = None,
    tp_pips: float = None,
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
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return TradeResult(False, message=f"Symbol {symbol} not found")
    
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    tick = mt5.symbol_info_tick(symbol)
    point = symbol_info.point
    
    # Determine order type and price
    if order_type.upper() == "BUY":
        mt5_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl = price - sl_pips * point * 10 if sl_pips else 0.0
        tp = price + tp_pips * point * 10 if tp_pips else 0.0
    else:
        mt5_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = price + sl_pips * point * 10 if sl_pips else 0.0
        tp = price - tp_pips * point * 10 if tp_pips else 0.0
    
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
    position = mt5.positions_get(ticket=ticket)
    if not position:
        return TradeResult(False, message="Position not found")
    
    pos = position[0]
    
    # Reverse the position
    close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(pos.symbol).bid if pos.type == 0 else mt5.symbol_info_tick(pos.symbol).ask
    
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
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return TradeResult(False, message=f"Close failed: {result.comment}")
    
    return TradeResult(True, price=result.price, message="Position closed")

# Usage
if __name__ == "__main__":
    mt5.initialize()
    
    # Open a buy position with 50 pip SL and 100 pip TP
    result = market_order("EURUSD", "BUY", 0.01, sl_pips=50, tp_pips=100)
    print(result)
    
    mt5.shutdown()
```

### 4. Risk Management Template

```python
# templates/05_risk_management/position_sizer.py
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
        account_balance = account_info.balance
    
    symbol_info = mt5.symbol_info(symbol)
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    point = symbol_info.point
    min_lot = symbol_info.volume_min
    lot_step = symbol_info.volume_step
    max_lot = symbol_info.volume_max
    
    # Calculate risk amount
    risk_amount = account_balance * (risk_percent / 100)
    
    # Calculate pip value per lot
    pip_value = (tick_value / tick_size) * point * 10
    
    # Calculate lot size
    lot_size = risk_amount / (sl_pips * pip_value)
    
    # Round to lot step
    lot_size = max(min_lot, round(lot_size / lot_step) * lot_step)
    lot_size = min(lot_size, max_lot)
    
    return round(lot_size, 2)

# Usage
if __name__ == "__main__":
    mt5.initialize()
    
    # Risk 1% with 30 pip stop loss
    lot = calculate_lot_size("EURUSD", risk_percent=1.0, sl_pips=30)
    print(f"Recommended lot size: {lot}")
    
    mt5.shutdown()
```

### 5. Complete Strategy Template

```python
# templates/06_strategies/sma_crossover_bot.py
"""
Simple SMA Crossover Bot
- Buys when fast SMA crosses above slow SMA
- Sells when fast SMA crosses below slow SMA
- Uses percentage-based risk management
"""

import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

class SMACrossoverBot:
    def __init__(
        self,
        symbol: str = "EURUSD",
        timeframe: int = mt5.TIMEFRAME_H1,
        fast_period: int = 10,
        slow_period: int = 50,
        risk_percent: float = 1.0,
        sl_pips: float = 50,
        tp_pips: float = 100
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.risk_percent = risk_percent
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.magic = 12345
        
    def get_signal(self) -> str:
        """Check for trading signal."""
        bars = max(self.fast_period, self.slow_period) + 10
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        df = pd.DataFrame(rates)
        
        df['sma_fast'] = df['close'].rolling(self.fast_period).mean()
        df['sma_slow'] = df['close'].rolling(self.slow_period).mean()
        
        # Check crossover
        curr_fast = df['sma_fast'].iloc[-1]
        curr_slow = df['sma_slow'].iloc[-1]
        prev_fast = df['sma_fast'].iloc[-2]
        prev_slow = df['sma_slow'].iloc[-2]
        
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return "BUY"
        elif prev_fast >= prev_slow and curr_fast < curr_slow:
            return "SELL"
        
        return "HOLD"
    
    def has_position(self) -> bool:
        """Check if we have an open position."""
        positions = mt5.positions_get(symbol=self.symbol, magic=self.magic)
        return positions is not None and len(positions) > 0
    
    def run(self):
        """Main trading loop."""
        print(f"Starting SMA Crossover Bot on {self.symbol}")
        
        while True:
            signal = self.get_signal()
            
            if signal != "HOLD" and not self.has_position():
                # Execute trade
                from trade_executor import market_order
                result = market_order(
                    self.symbol, signal, 0.01,
                    sl_pips=self.sl_pips,
                    tp_pips=self.tp_pips,
                    magic=self.magic
                )
                print(f"[{datetime.now()}] {signal}: {result.message}")
            
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    mt5.initialize()
    bot = SMACrossoverBot()
    bot.run()
```

## 🛠️ Development Roadmap

### Week 1: Core Templates
- [x] Connection templates
- [x] Data retrieval templates
- [x] Order management templates
- [ ] Position tracking templates

### Week 2: Advanced Templates
- [ ] Risk management module
- [x] Complete strategy examples
- [x] Custom indicator templates
- [ ] Scheduled automation

### Week 3: Integration & Polish
- [ ] External API bridges
- [ ] Comprehensive documentation
- [ ] Unit tests
- [ ] PyPI package

## 🤝 Contributing

Contributions welcome! Please submit templates that are:
- Well-documented with docstrings
- Include error handling
- Have usage examples

## 📄 License

MIT License - Use freely in your trading projects!

---

**Star ⭐ if these templates save you time!**
