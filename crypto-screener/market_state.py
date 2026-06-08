from binance_api import get_klines_cached

from indicator import (
    prepare_dataframe,
    ema20,
    ema50
)


def get_market_state():

    klines = get_klines_cached(
        "BTCUSDT",
        interval="4h",
        limit=100
    )

    df = prepare_dataframe(
        klines
    )

    e20 = ema20(df)

    e50 = ema50(df)

    price = df["close"].iloc[-1]

    if price > e20 > e50:

        return {
            "state": "BULL",
            "multiplier": 1.2
        }

    elif price < e20 < e50:

        return {
            "state": "BEAR",
            "multiplier": 0.7
        }

    else:

        return {
            "state": "SIDEWAYS",
            "multiplier": 1.0
        }