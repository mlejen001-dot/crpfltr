def filter_coins(data):

    result = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            # hanya pair USDT
            if not symbol.endswith("USDT"):
                continue

            volume = float(coin["quoteVolume"])

            # volume minimal 10 juta USD
            if volume < 10_000_000:
                continue

            result.append(coin)

        except Exception:
            pass

    return result