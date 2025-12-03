import time
import requests
from app.ai.trading_bot import TradingBot

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

def fetch_binance_closes(symbol="BTCUSDT", interval="1d", limit=500):
    """
    Returns a list of floats (close prices).
    """
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(BINANCE_KLINES, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # kline structure: [ openTime, open, high, low, close, ... ]
    closes = [float(k[4]) for k in data]
    return closes

def pretty_report(result):
    print("\nBacktest report")
    print("----------------")
    print(f"Initial capital: {result.get('initial_capital')}")
    print(f"Final value:     {result.get('final_value')}")
    print(f"Return %:        {result.get('return_pct') or result.get('total_return_pct', 'N/A')}")
    print(f"Total trades:    {len(result.get('trade_log', result.get('trades', [])))}")
    trades = result.get('trade_log') or result.get('trades') or []
    if trades:
        print("\nSample trades:")
        for t in trades[:10]:
            print(f"  {t}")
    else:
        print("\nNo trades were executed (HOLD throughout).")

def run_test_with_binance(symbol="BTCUSDT"):
    print(f"Fetching {symbol} daily closes from Binance...")
    closes = fetch_binance_closes(symbol=symbol, interval="1d", limit=500)
    print(f"Fetched {len(closes)} closes. Running backtest...")

    bot = TradingBot(ma_short=5, ma_long=20)
    result = bot.backtest(prices=closes, initial_capital=1000.0, fee_pct=0.001)

    pretty_report(result)

if __name__ == "__main__":
    run_test_with_binance("BTCUSDT")
