def detect_choch(df):

    if len(df) < 20:
        return False

    highs = df["high"]
    close = df["close"]

    lookback_high = highs.iloc[-15:-1].max()

    return close.iloc[-1] > lookback_high


def detect_bos(df):

    if len(df) < 30:
        return False

    highs = df["high"]

    previous_high = highs.iloc[-30:-15].max()

    recent_high = highs.iloc[-15:].max()

    return recent_high > previous_high