def flow_state(
    p1,
    oi1
):

    if p1 > 0.5 and oi1 > 0.5:
        return "LONG_BUILD"

    if p1 < -0.5 and oi1 > 0.5:
        return "SHORT_BUILD"

    if p1 > 0.5 and oi1 < -0.5:
        return "SHORT_COVER"

    if p1 < -0.5 and oi1 < -0.5:
        return "LONG_LIQUIDATION"

    return "NEUTRAL"