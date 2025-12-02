import ccxt
import pandas as pd

def fetch_ohlcv(symbol="BTC/USDT", timeframe="5m", limit=200):
    exchange = ccxt.binance({"enableRateLimit": True})
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df.set_index("ts")

if __name__ == "__main__":
    df = fetch_ohlcv()
    print(df.tail())
