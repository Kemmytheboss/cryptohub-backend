import requests
import time
import pandas as pd

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

def fetch_binance_klines(symbol="BTCUSDT", interval="1d", limit=500):
    """
    Returns pandas Series of close prices and timestamps.
    """
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(BINANCE_KLINES, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    # kline format: [openTime, open, high, low, close, ...]
    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","num_trades","taker_base_vol","taker_quote_vol","ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df[["open_time","close"]]
