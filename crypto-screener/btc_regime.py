from oi import oi_change_1h
from oi import oi_change_4h


def btc_regime():

    oi1 = oi_change_1h(
        "BTCUSDT"
    )

    oi4 = oi_change_4h(
        "BTCUSDT"
    )

    if oi1 > 2 and oi4 > 5:
        return "RISK_ON"

    if oi1 < -2 and oi4 < -5:
        return "RISK_OFF"

    return "NEUTRAL"