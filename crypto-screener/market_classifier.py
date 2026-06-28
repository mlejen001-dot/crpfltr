def classify_coin(
    rs,
    oi1,
    oi4,
    oi24,
    accel,
    momentum,
    flow,
    choch,
    bos,
    p4
):

    # ==========================
    # TREND LEADER
    # ==========================

    if (
        bos
        and (
            rs > 5
            or oi24 > 8
        )
        and flow == "LONG_BUILD"
    ):
        return "TREND_LEADER"

    # ==========================
    # REVERSAL
    # ==========================

    if (
        choch
        and (
            oi1 > 0
            or oi4 > 0
        )
    ):
        return "REVERSAL"

    # ==========================
    # EARLY TREND
    # ==========================

    if (
        oi1 > 0
        and oi4 > 0
        and accel > 0
        and p4 > 0
        and momentum in ("UPTREND", "ACCELERATING")
    ):
        return "EARLY_TREND"

    return "IGNORE"