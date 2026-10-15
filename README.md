# 🐍 MT5-Python-Templates

> Small, readable Python templates for MetaTrader 5 development. Copy, customize, trade.

[![CI](https://github.com/Caesarcph/mt5-python-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/Caesarcph/mt5-python-templates/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![MT5](https://img.shields.io/badge/MetaTrader-5-orange.svg)](https://www.metatrader5.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📌 Status

**Early-stage template collection.** Nine small, single-file templates (01–09) exist today, one per folder.
They are starting points to copy and adapt, not a library or framework:

- There are **no unit tests** yet. CI only checks that every template compiles (`python -m compileall`),
  because the `MetaTrader5` package installs only on Windows.
- The templates have not been verified against every broker. Run them on a **demo account** first.
- Templates are run as standalone scripts; they are not packaged for `pip install`.

Planned work (tests, more templates, packaging, docs) is tracked in [ROADMAP.md](ROADMAP.md).

## 🎯 Why This Repository?

MT5's Python integration is powerful but poorly documented. This repo collects small, commented templates so you can:

- ✅ Skip boilerplate setup
- ✅ See the common MT5 calls (`initialize`, `copy_rates_*`, `order_send`, `positions_get`) used in context
- ✅ Have a starting point to adapt for your own scripts

## 📦 Templates Included

```
templates/
├── 01_connection/           # basic_connect.py          - connect / disconnect, print account info
├── 02_data_retrieval/       # get_ohlcv.py              - OHLCV history as DataFrame, latest tick
├── 03_order_management/     # trade_executor.py         - market order with SL/TP, close by ticket
├── 04_position_tracking/    # open_positions.py         - summarize open positions
├── 05_risk_management/      # position_sizer.py         - lot size from risk % and SL pips
├── 06_strategies/           # sma_crossover_bot.py      - SMA crossover signal loop (prints signals only)
├── 07_indicators/           # rsi.py                    - RSI on a pandas Series / DataFrame
├── 08_automation/           # scheduled_signal_check.py - run a signal check on a fixed interval
└── 09_integration/          # webhook_signal_bridge.py  - turn a webhook-style payload into a market order
```

Each folder also has an `__init__.py`.

## 🚀 Quick Start

Requirements: Windows with the MetaTrader 5 terminal installed and logged in (demo account recommended),
Python 3.10+.

```bash
# Clone
git clone https://github.com/Caesarcph/mt5-python-templates.git
cd mt5-python-templates

# Install
pip install MetaTrader5 pandas

# Test connection
python templates/01_connection/basic_connect.py
```

`templates/07_indicators/rsi.py` only needs `pandas` and runs on any OS:

```bash
python templates/07_indicators/rsi.py
```

## 📚 Template Reference

Short summaries of what each template actually does. See the source files for the full code.

### 1. Connection Templates

`templates/01_connection/basic_connect.py`

- `connect_mt5(path=None, login=None, password=None, server=None, timeout=60000) -> bool`
  calls `mt5.initialize()` with only the arguments you pass, then prints server, login, balance and leverage.
  Returns `False` (and prints `mt5.last_error()`) on failure.
- `disconnect_mt5()` calls `mt5.shutdown()`.

### 2. Data Retrieval Templates

`templates/02_data_retrieval/get_ohlcv.py`

- `get_ohlcv(symbol, timeframe=mt5.TIMEFRAME_H1, bars=1000, start_time=None) -> pd.DataFrame`
  returns `open, high, low, close, tick_volume` indexed by time (empty DataFrame on failure).
- `get_latest_tick(symbol) -> dict | None` returns `time, bid, ask, spread, volume, flags`.
  Note: `spread` is estimated as `(ask - bid) * 10000`, which is only meaningful for standard 4/5-digit FX pairs.

```python
df = get_ohlcv("EURUSD", mt5.TIMEFRAME_H1, 500)
tick = get_latest_tick("EURUSD")
```

### 3. Order Management Templates

`templates/03_order_management/trade_executor.py`

- `market_order(symbol, order_type, volume, sl_pips=None, tp_pips=None, comment="", magic=0) -> TradeResult`
  sends a market `BUY`/`SELL` with optional SL/TP converted from pips (`1 pip = 10 * point`).
- `close_position(ticket, comment="") -> TradeResult` closes a position with an opposite market deal.
- Uses `ORDER_FILLING_IOC` and a fixed `deviation` of 20; some brokers require a different filling mode.
- The `__main__` block only initializes and shuts down; the example order is commented out.

```python
result = market_order("EURUSD", "BUY", 0.01, sl_pips=50, tp_pips=100)
print(result.success, result.message)
```

### 4. Position Tracking Template

`templates/04_position_tracking/open_positions.py`

- `get_open_positions_summary(symbol=None) -> list[dict]` returns ticket, symbol, type, volume,
  open/current price, profit, swap and comment for each open position.

### 5. Risk Management Template

`templates/05_risk_management/position_sizer.py`

- `calculate_lot_size(symbol, risk_percent, sl_pips, account_balance=None) -> float`
  computes lot size from `risk_percent` of the balance and the SL distance, using the symbol's tick value / tick size,
  then rounds to the broker's `volume_step` and clamps to `volume_min` / `volume_max`. Returns `0.0` if inputs or MT5 data are invalid.

```python
lot = calculate_lot_size("EURUSD", risk_percent=1.0, sl_pips=30)
```

### 6. Strategy Template

`templates/06_strategies/sma_crossover_bot.py`

- `SMACrossoverBot(symbol="EURUSD", timeframe=mt5.TIMEFRAME_M15, fast_period=10, slow_period=30)`
- `get_signal()` returns a `CrossoverSignal(action, price)` with `BUY` / `SELL` / `HOLD` based on a fast/slow SMA cross.
- `run(poll_seconds=60)` loops forever and **prints** signals. It does **not** place orders;
  combine it with `trade_executor.market_order` and `position_sizer.calculate_lot_size` yourself if you want execution.

### 7. Indicator Template

`templates/07_indicators/rsi.py`

- `calculate_rsi(close, period=14) -> pd.Series` (Wilder-style smoothing via `ewm`).
- `add_rsi_column(df, period=14) -> pd.DataFrame` returns a copy with an `rsi` column.

### 8. Automation Template

`templates/08_automation/scheduled_signal_check.py`

- `run_every(interval_seconds, check_fn)` calls `check_fn()` on a fixed interval and prints non-`HOLD` signals.
- `simple_price_action_signal(symbol="EURUSD")` is an example signal that compares the last two H1 closes.

### 9. Integration Template

`templates/09_integration/webhook_signal_bridge.py`

- `execute_webhook_signal(payload) -> BridgeResult` validates a dict like
  `{"symbol": "EURUSD", "side": "BUY", "volume": 0.01, "comment": "..."}` and sends a market order (no SL/TP).
- No HTTP server is included: plug the function into your own web framework's request handler.

## 🛠️ Development Roadmap

### Week 1: Core Templates
- [x] Connection templates
- [x] Data retrieval templates
- [x] Order management templates
- [x] Position tracking templates

### Week 2: Advanced Templates
- [x] Risk management (basic position sizer)
- [x] Strategy example (SMA crossover, signal only)
- [x] Indicator template (RSI)
- [x] Scheduled automation

### Week 3: Integration & Polish
- [x] Webhook payload bridge (basic)
- [ ] Comprehensive documentation (planned)
- [ ] Unit tests (planned)
- [ ] PyPI package (planned)

Details in [ROADMAP.md](ROADMAP.md).

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md). Please submit templates that are:
- Well-documented with docstrings
- Include error handling
- Have usage examples

## 📄 License

[MIT License](LICENSE) - Use freely in your trading projects!

---

**Star ⭐ if these templates save you time!**
