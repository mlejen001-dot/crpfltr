def classify_coin(
    rs,
    rsi,
    oi1,
    oi4,
    accel,
    momentum,
    flow
):

    if (
        rs > 10
        and accel > 5
        and momentum in [
            "UPTREND",
            "ACCELERATING"
        ]
    ):
        return "TREND_LEADER"

    if (
        rs > 0
        and oi1 > 0
        and accel > 0
    ):
        return "EARLY_TREND"

    if (
        momentum == "REVERSAL"
        and accel > 0
    ):
        return "REVERSAL"

    return "IGNORE"