def flow_state(
    p1,
    oi1
):

    if p1 > 0 and oi1 > 0:
        return "LONG_BUILD"

    elif p1 < 0 and oi1 > 0:
        return "SHORT_BUILD"

    elif p1 > 0 and oi1 < 0:
        return "SHORT_COVER"

    elif p1 < 0 and oi1 < 0:
        return "LONG_LIQUIDATION"

    return "NEUTRAL"