def classify_coin(
    rs,
    oi1,
    oi4,
    oi24,
    accel,
    momentum,
    flow,
    choch,
    bos
):

    # sudah breakout

    if (
        bos
        and rs > 10
        and oi24 > 10
    ):
        return "TREND_LEADER"

    # baru reversal

    if (
        choch
        and oi1 > 0
        and oi4 > 0
    ):
        return "REVERSAL"

    # akumulasi sebelum breakout

    if (
        oi4 > 0
        and oi1 > 0
        and accel > 0
    ):
        return "EARLY_TREND"

    return "IGNORE"