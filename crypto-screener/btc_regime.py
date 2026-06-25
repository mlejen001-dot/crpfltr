from oi import oi_change_1h
from oi import oi_change_4h


def btc_regime():

    oi1 = oi_change_1h(
        "BTCUSDT"
    )

    oi4 = oi_change_4h(
        "BTCUSDT"
    )

    score = oi1 + oi4

    if score > 3:
        return "RISK_ON"

    if score < -3:
        return "RISK_OFF"

    return "NEUTRAL"