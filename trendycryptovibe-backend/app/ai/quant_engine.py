import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List
from .indicators import add_indicators

def compute_metrics(equity_curve: List[float], initial_capital: float, trade_pnls: List[float], periods_per_year=252):
    # equity_curve is list of portfolio values per step
    returns = pd.Series(equity_curve).pct_change().fillna(0)
    total_return = (equity_curve[-1] / initial_capital - 1.0) * 100
    # CAGR estimate
    n_years = len(equity_curve) / periods_per_year
    cagr = ((equity_curve[-1] / initial_capital) ** (1 / max(n_years, 1e-9)) - 1) * 100 if n_years>0 else 0.0
    # Sharpe (annualized) - use sample std
    if returns.std() == 0:
        sharpe = 0.0
    else:
        sharpe = (returns.mean() / returns.std()) * math.sqrt(periods_per_year)
    # Max Drawdown
    ser = pd.Series(equity_curve)
    roll_max = ser.cummax()
    drawdowns = (ser - roll_max) / roll_max
    max_dd = drawdowns.min() * 100
    # Win rate
    wins = len([p for p in trade_pnls if p>0])
    losses = len([p for p in trade_pnls if p<=0])
    win_rate = wins / max(1, (wins+losses)) * 100
    return {
        "total_return_pct": round(total_return, 6),
        "cagr_pct": round(cagr, 6),
        "sharpe": round(sharpe, 4),
        "max_drawdown_pct": round(max_dd, 4),
        "win_rate_pct": round(win_rate, 2)
    }

class QuantEngine:
    def __init__(self, ma_short=5, ma_long=20, rsi_period=14, fee_pct=0.001):
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.rsi_period = rsi_period
        self.fee_pct = fee_pct

    def signal_row(self, row):
        # simple rule: MA crossover + RSI filter
        if row[f"ma_{self.ma_short}"] > row[f"ma_{self.ma_long}"] and row["rsi"] < 70:
            return "BUY"
        if row[f"ma_{self.ma_short}"] < row[f"ma_{self.ma_long}"] and row["rsi"] > 30:
            return "SELL"
        return "HOLD"

    def backtest_df(self, df: pd.DataFrame, initial_capital=1000.0, stop_loss=None, take_profit=None, fixed_size=None):
        """
        df: must contain 'close' and will have indicators added
        stop_loss/take_profit are fractions (e.g., 0.05)
        fixed_size: if provided, buy this fraction of capital each buy (0-1)
        """
        df = add_indicators(df, ma_short=self.ma_short, ma_long=self.ma_long, rsi_period=self.rsi_period).reset_index(drop=True)
        cash = initial_capital
        position = 0.0
        position_entry_price = None
        equity_curve = []
        trades = []
        trade_pnls = []

        for i, row in df.iterrows():
            price = float(row["close"])
            sig = self.signal_row(row)

            # Manage existing position (stop/tp)
            if position > 0 and position_entry_price is not None:
                # stop loss
                if stop_loss and price <= position_entry_price * (1 - stop_loss):
                    proceeds = position * price * (1 - self.fee_pct)
                    cash += proceeds
                    pnl = proceeds - 0  # cash was zero when we bought in full-size version
                    trade_pnls.append((proceeds - 0))  # crude
                    trades.append({"type":"sell","price":price,"index":i,"position":position})
                    position = 0.0
                    position_entry_price = None
                # take profit
                elif take_profit and price >= position_entry_price * (1 + take_profit):
                    proceeds = position * price * (1 - self.fee_pct)
                    cash += proceeds
                    trade_pnls.append((proceeds - 0))
                    trades.append({"type":"sell","price":price,"index":i,"position":position})
                    position = 0.0
                    position_entry_price = None

            # Signals
            if sig == "BUY" and cash > 0:
                # Determine buy size
                if fixed_size:
                    spend = cash * fixed_size
                else:
                    spend = cash
                qty = (spend / price) * (1 - self.fee_pct)
                if qty > 0:
                    position += qty
                    position_entry_price = price
                    trades.append({"type":"buy","price":price,"index":i,"position":qty})
                    cash -= spend  # we spent the capital

            elif sig == "SELL" and position > 0:
                proceeds = position * price * (1 - self.fee_pct)
                pnl = proceeds - 0
                trade_pnls.append(pnl)
                trades.append({"type":"sell","price":price,"index":i,"position":position})
                cash += proceeds
                position = 0
                position_entry_price = None

            equity = cash + position * price
            equity_curve.append(equity)

        final_val = cash + position * df.iloc[-1]["close"]
        metrics = compute_metrics(equity_curve, initial_capital, trade_pnls)
        return {
            "initial_capital": initial_capital,
            "final_value": round(final_val, 6),
            "equity_curve": equity_curve,
            "trades": trades,
            "trade_pnls": trade_pnls,
            **metrics
        }
