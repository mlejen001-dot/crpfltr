import pandas as pd


def prepare_dataframe(klines):

    df = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "tb_base",
            "tb_quote",
            "ignore"
        ]
    )

    df["close"] = df["close"].astype(float)

    df["volume"] = df["volume"].astype(float)

    return df
def ema20(df):

    return (
        df["close"]
        .ewm(span=20)
        .mean()
        .iloc[-1]
    )


def ema50(df):

    return (
        df["close"]
        .ewm(span=50)
        .mean()
        .iloc[-1]
    )
def rsi(df, period=14):

    delta = df["close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = (
        gain
        .rolling(period)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(period)
        .mean()
    )

    rs = avg_gain / avg_loss

    rsi = (
        100 -
        (100 / (1 + rs))
    )

    return round(
        rsi.iloc[-1],
        2
    )
def volume_spike(df):

    current = df["volume"].iloc[-1]

    average = (
        df["volume"]
        .tail(20)
        .mean()
    )

    return current / average