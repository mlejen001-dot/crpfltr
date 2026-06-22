def oi_signal(
    price_change,
    oi_change
):

    if price_change > 0 and oi_change > 0:
        return "LONG_BUILDUP"

    if price_change < 0 and oi_change > 0:
        return "SHORT_BUILDUP"

    if price_change > 0 and oi_change < 0:
        return "SHORT_COVERING"

    if price_change < 0 and oi_change < 0:
        return "LONG_LIQUIDATION"

    return "NEUTRAL"