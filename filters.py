from whitelist import ALLOWED

def filter_coins(data):

    result = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            if not symbol.endswith("USDT"):
                continue

            base_symbol = symbol.replace(
                "USDT",
                ""
            )

            if base_symbol not in ALLOWED:
                continue

            volume = float(
                coin["quoteVolume"]
            )

            if volume < 10_000_000:
                continue

            result.append(coin)

        except Exception:
            pass

    return result