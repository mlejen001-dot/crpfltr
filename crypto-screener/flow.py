def flow_state(
    p1,
    oi1
):

    if p1 > 1 and oi1 > 1:
        return "LONG_BUILD"

    if p1 < -1 and oi1 > 1:
        return "SHORT_BUILD"

    if p1 > 1 and oi1 < -1:
        return "SHORT_COVER"

    if p1 < -1 and oi1 < -1:
        return "LONG_LIQUIDATION"

    return "NEUTRAL"