from binance_api import get_exchange_info
import time


def build_universe():

    info = get_exchange_info()

    universe = set()

    now = int(time.time() * 1000)

    MIN_AGE_DAYS = 60

    for symbol in info["symbols"]:

        try:

            if symbol["status"] != "TRADING":
                continue

            if symbol["quoteAsset"] != "USDT":
                continue

            age_days = (
                now - int(symbol["onboardDate"])
            ) / (1000 * 60 * 60 * 24)

            if age_days < MIN_AGE_DAYS:
                continue

            universe.add(symbol["symbol"])

        except:
            pass

    return universe