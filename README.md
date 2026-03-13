# QC Mean Reversion Strategy

Simple mean-reversion trading algorithm for QuantConnect (Python).

## Strategy Overview
- Asset: SPY ETF (daily resolution)
- Entry: Price deviates > 1.5 std from 50-day SMA
- Exit: Price returns within 0.2 std of SMA
- Backtest: [Link to your QC backtest if you have public one]

## Files
- `main.py`: The full QuantConnect algorithm code

## How to Run
1. Create new Python algorithm in QuantConnect
2. Paste `main.py` content
3. Backtest and tweak parameters (e.g., entry_z = 2.0)

For quant research interviews/portfolio.