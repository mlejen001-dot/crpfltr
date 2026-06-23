def classify_coin(
    rs,
    oi1,
    oi4,
    oi24,
    accel,
    momentum,
    flow
):

    # =====================
    # TREND LEADER
    # =====================

    if (
        rs > 10
        and oi24 > 10
        and accel > 5
        and flow == "LONG_BUILD"
    ):
        return "TREND_LEADER"

    # =====================
    # EARLY TREND
    # =====================

    if (
        oi1 > 0
        and oi4 > 0
        and accel > 0
        and oi24 > 0
    ):
        return "EARLY_TREND"

    # =====================
    # REVERSAL
    # =====================

    if (
        oi1 > 0
        and accel > 0
        and momentum == "REVERSAL"
    ):
        return "REVERSAL"

    return "IGNORE"