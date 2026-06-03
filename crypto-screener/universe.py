def build_universe(data):

    universe = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            if not symbol.endswith("USDT"):
                continue

            volume = float(
                coin["quoteVolume"]
            )

            if volume < 50_000_000:
                continue

            universe.append(coin)

        except:
            pass

    return universe