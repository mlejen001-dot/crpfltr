from binance_api import (
    get_klines_cached
)

from indicator import (
    prepare_dataframe
)


def _price_change(
    symbol,
    interval
):

    try:

        klines = get_klines_cached(
            symbol,
            interval=interval,
            limit=2
        )

        df = prepare_dataframe(
            klines
        )

        current = df["close"].iloc[-1]

        previous = df["close"].iloc[-2]

        return round(
            ((current - previous)
             / previous) * 100,
            2
        )

    except Exception:

        return 0


def price_change_1h(symbol):

    return _price_change(
        symbol,
        "1h"
    )


def price_change_4h(symbol):

    return _price_change(
        symbol,
        "4h"
    )


def price_change_24h(symbol):

    return _price_change(
        symbol,
        "1d"
    )


def acceleration_score(
    p24,
    p4,
    p1
):

    score = (
        (p24 * 1)
        + (p4 * 2)
        + (p1 * 3)
    )

    return round(
        score,
        2
    )

    score = (
        (p24 * 1)
        + (p4 * 2)
        + (p1 * 3)
    )

    return round(
        score,
        2
    )


def momentum_state(
    p24,
    p4,
    p1
):

    if p24 > 0 and p4 > 0 and p1 > 0:

        if p1 > p4:
            return "ACCELERATING"

        return "UPTREND"

    if p24 > 0 and p4 > 0 and p1 < 0:

        return "EXHAUSTION"

    if p24 < 0 and p4 > 0 and p1 > 0:

        return "REVERSAL"

    if p24 < 0 and p4 < 0 and p1 < 0:

        return "DOWNTREND"

    return "NEUTRAL"