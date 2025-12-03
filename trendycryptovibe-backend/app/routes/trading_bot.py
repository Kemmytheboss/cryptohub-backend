from fastapi import APIRouter, Body
from typing import List, Dict, Any
from app.ai.trading_bot import TradingBot

router = APIRouter(prefix="/bot", tags=["TradingBot"])
bot = TradingBot(ma_short=5, ma_long=20)


@router.post("/signal")
def get_signal(prices: Dict[str, List[float]] = Body(...)):
    """
    Expect JSON body:
    {
      "prices": [100.0, 101.2, 100.5, ...]
    }
    Returns combined signal and details.
    """
    prices_list = prices.get("prices") or prices.get("data") or []

    if not isinstance(prices_list, list) or len(prices_list) == 0:
        return {"error": "Provide a non-empty list under 'prices'."}

    out = bot.combined_signal(prices_list)
    return out


@router.post("/backtest")
def run_backtest(payload: Dict[str, Any] = Body(...)):
    """
    Expect:
    {
      "prices": [...],
      "initial_capital": 1000,
      "fee_pct": 0.001
    }
    """
    prices = payload.get("prices", [])
    initial_capital = float(payload.get("initial_capital", 1000.0))
    fee_pct = float(payload.get("fee_pct", 0.0))

    # FIXED CONDITION
    if not isinstance(prices, list) or len(prices) == 0:
        return {"error": "Provide a non-empty list under 'prices'."}

    # Run backtest from the bot class
    result = bot.backtest(
        prices=prices,
        initial_capital=initial_capital,
        fee_pct=fee_pct,
    )

    return {
        "initial_capital": initial_capital,
        "fee_pct": fee_pct,
        "result": result
    }
