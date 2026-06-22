from binance_api import get_open_interest_hist


def _calculate_change(current, previous):

    if previous == 0:
        return 0

    return round(
        ((current - previous) / previous) * 100,
        2
    )


def _oi_change(
    symbol,
    period
):

    data = get_open_interest_hist(
        symbol,
        period=period,
        limit=2
    )

    if not isinstance(data, list):
        return 0

    if len(data) < 2:
        return 0

    current = float(
        data[-1]["sumOpenInterest"]
    )

    previous = float(
        data[-2]["sumOpenInterest"]
    )

    return _calculate_change(
        current,
        previous
    )


def oi_change_1h(symbol):

    return _oi_change(
        symbol,
        "1h"
    )


def oi_change_4h(symbol):

    return _oi_change(
        symbol,
        "4h"
    )


def oi_change_24h(symbol):

    return _oi_change(
        symbol,
        "1d"
    )