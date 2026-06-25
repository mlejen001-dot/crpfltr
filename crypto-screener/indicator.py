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

    df["open"] = df["open"].astype(float)

    df["high"] = df["high"].astype(float)

    df["low"] = df["low"].astype(float)

    df["close"] = df["close"].astype(float)

    df["volume"] = df["volume"].astype(float)

    return df


def ema20(df):

    return (
        df["close"]
        .ewm(span=20, adjust=False)
        .mean()
        .iloc[-1]
    )


def ema50(df):

    return (
        df["close"]
        .ewm(span=50, adjust=False)
        .mean()
        .iloc[-1]
    )


def rsi(df, period=14):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

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

    rsi_value = (
        100 -
        (100 / (1 + rs))
    )

    return round(
        rsi_value.iloc[-1],
        2
    )


def volume_spike(df):

    current_volume = (
        df["volume"]
        .iloc[-2]
    )

    average_volume = (
        df["volume"]
        .iloc[-22:-2]
        .mean()
    )

    return round(
        current_volume /
        average_volume,
        2
    )


def trend_strength(df):

    e20 = ema20(df)

    e50 = ema50(df)

    if e20 > e50:
        return 1

    return 0


def price_above_ema20(df):

    price = (
        df["close"]
        .iloc[-2]
    )

    e20 = ema20(df)

    return price > e20


def volume_expansion(df):

    recent = (
        df["volume"]
        .iloc[-6:-1]
        .mean()
    )

    older = (
        df["volume"]
        .iloc[-26:-6]
        .mean()
    )

    return round(
        recent / older,
        2
    )