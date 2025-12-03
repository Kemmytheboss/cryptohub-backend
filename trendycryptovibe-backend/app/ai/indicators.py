import pandas as pd
import numpy as np
import ta  

def add_indicators(df, ma_short=5, ma_long=20, rsi_period=14):
    df = df.copy()
    df[f"ma_{ma_short}"] = df["close"].rolling(ma_short).mean()
    df[f"ma_{ma_long}"] = df["close"].rolling(ma_long).mean()
    df["rsi"] = ta.momentum.rsi(df["close"], window=rsi_period)
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    boll = ta.volatility.BollingerBands(df["close"])
    df["bb_h"] = boll.bollinger_hband()
    df["bb_l"] = boll.bollinger_lband()
    df = df.fillna(method="bfill").fillna(method="ffill")
    return df
