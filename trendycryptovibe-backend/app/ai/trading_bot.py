# app/ai/trading_bot.py
from typing import List, Dict, Any, Tuple
from statistics import mean, stdev

class TradingBot:
    """
    Simple multi-strategy trading bot.
    Strategies:
      - momentum: compares recent percent changes
      - ma_crossover: short/long moving average crossover
      - volatility: uses recent stddev to prefer hold when too volatile
    Combined signal is derived from weighted votes.
    """

    def __init__(self, ma_short: int = 5, ma_long: int = 20):
        if ma_short >= ma_long:
            raise ValueError("ma_short should be less than ma_long")
        self.ma_short = ma_short
        self.ma_long = ma_long

    # ---- helpers ----
    @staticmethod
    def pct_change(curr: float, prev: float) -> float:
        if prev == 0:
            return 0.0
        return (curr - prev) / prev * 100

    @staticmethod
    def moving_average(data: List[float], window: int) -> float:
        if len(data) < window or window <= 0:
            return mean(data) if data else 0.0
        return mean(data[-window:])

    @staticmethod
    def volatility(data: List[float], window: int) -> float:
        if len(data) < max(2, window):
            return 0.0
        return stdev(data[-window:])

    # ---- strategies ----
    def momentum_signal(self, prices: List[float]) -> str:
        """
        Momentum: compare last two pct changes.
        If avg recent % change > +threshold => buy
        if < -threshold => sell
        else hold
        """
        if len(prices) < 3:
            return "hold"
        p0, p1, p2 = prices[-3], prices[-2], prices[-1]
        ch1 = self.pct_change(p1, p0)
        ch2 = self.pct_change(p2, p1)
        avg = (ch1 + ch2) / 2
        if avg > 1.5:
            return "buy"
        if avg < -1.5:
            return "sell"
        return "hold"

    def ma_crossover_signal(self, prices: List[float]) -> str:
        """
        Simple moving average crossover:
        - buy when short MA crosses above long MA
        - sell when short MA crosses below long MA
        - hold otherwise
        Uses the last two points to detect cross.
        """
        if len(prices) < self.ma_long + 1:
            return "hold"
        ma_short_prev = self.moving_average(prices[:-1], self.ma_short)
        ma_long_prev = self.moving_average(prices[:-1], self.ma_long)
        ma_short_now = self.moving_average(prices, self.ma_short)
        ma_long_now = self.moving_average(prices, self.ma_long)

        # cross detection
        prev_diff = ma_short_prev - ma_long_prev
        now_diff = ma_short_now - ma_long_now

        if prev_diff <= 0 and now_diff > 0:
            return "buy"
        if prev_diff >= 0 and now_diff < 0:
            return "sell"
        return "hold"

    def volatility_filter(self, prices: List[float]) -> float:
        """
        Returns volatility (stddev) of recent prices (ma_long window).
        Higher volatility reduces confidence in signals.
        """
        vol = self.volatility(prices, self.ma_long)
        return vol

    # ---- ensemble / combined signal ----
    def combined_signal(self, prices: List[float], weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Evaluate all strategies, produce a combined score and final signal.
        weights: dict with keys 'momentum', 'ma', 'volatility' used for scoring.
        Returns:
          {
            "momentum": "buy|sell|hold",
            "ma": "buy|sell|hold",
            "volatility": float,
            "score": float,  # positive => buy, negative => sell
            "signal": "buy|sell|hold",
            "details": {...}
          }
        """
        if weights is None:
            weights = {"momentum": 0.5, "ma": 0.4, "volatility": -0.1}

        m = self.momentum_signal(prices)
        ma = self.ma_crossover_signal(prices)
        vol = self.volatility_filter(prices)

        # map signals to numeric votes
        mapping = {"buy": 1.0, "hold": 0.0, "sell": -1.0}
        m_vote = mapping.get(m, 0.0)
        ma_vote = mapping.get(ma, 0.0)

        # volatility reduces magnitude proportional to vol / (avg price)
        avg_price = mean(prices[-self.ma_long:]) if len(prices) >= self.ma_long else mean(prices) if prices else 1.0
        vol_factor = 0.0
        if avg_price and avg_price > 0:
            vol_factor = (vol / avg_price)  # small number

        # composite score
        score = weights["momentum"] * m_vote + weights["ma"] * ma_vote + weights["volatility"] * (-vol_factor)

        # threshold to decide final signal
        if score > 0.25:
            final = "buy"
        elif score < -0.25:
            final = "sell"
        else:
            final = "hold"

        return {
            "momentum": m,
            "ma": ma,
            "volatility": vol,
            "score": score,
            "signal": final,
            "details": {
                "m_vote": m_vote,
                "ma_vote": ma_vote,
                "vol_factor": vol_factor,
                "avg_price": avg_price
            }
        }

    # ---- simple backtester ----
    def backtest(self, prices: List[float], initial_capital: float = 1000.0, fee_pct: float = 0.0) -> Dict[str, Any]:
        """
        Run a single-pass backtest over the price series using the combined signal at each step.
        Strategy:
          - At each step (starting from ma_long), compute combined signal with history up to this point.
          - If signal == 'buy' and we are in cash -> buy with all capital (no leverage)
          - If signal == 'sell' and we are holding -> sell all holdings to cash
          - Hold otherwise
        Returns a report with final portfolio value and trades.
        NOTE: very naive (no slippage modeling, discrete timestamps).
        """
        cash = initial_capital
        position = 0.0  # number of coins held
        trades = []

        # iterate from index = ma_long to end
        for i in range(self.ma_long, len(prices)):
            window = prices[: i + 1]  # up-to current
            res = self.combined_signal(window)
            price = prices[i]
            signal = res["signal"]

            # buy
            if signal == "buy" and cash > 0:
                # buy as much as possible
                amount = (cash * (1 - fee_pct))
                position = amount / price
                cash = 0.0
                trades.append({"type": "buy", "price": price, "index": i, "position": position})

            # sell
            elif signal == "sell" and position > 0:
                proceeds = position * price * (1 - fee_pct)
                cash = proceeds
                trades.append({"type": "sell", "price": price, "index": i, "position": position})
                position = 0.0

            # else hold

        # finalize current portfolio value
        final_value = cash + position * prices[-1]
        return {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return_pct": ((final_value - initial_capital) / initial_capital) * 100,
            "trades": trades
        }
