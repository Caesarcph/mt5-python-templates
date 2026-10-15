# Roadmap

## Done

- 01–09 single-file templates: connection, data retrieval, order management, position tracking,
  risk-based position sizing, SMA crossover signal loop, RSI indicator, scheduled signal check,
  webhook payload bridge.
- CI compile check (`python -m compileall templates`).

## Planned

- Unit tests that mock the `MetaTrader5` module so they can run on Linux CI.
- Optional order execution in the SMA crossover template (currently prints signals only).
- More templates (e.g. pending orders, modifying SL/TP, trade history export).
- More complete documentation per template.
- PyPI package.
