def filter_coins(data, universe):

    MIN_VOLUME = 5_000_000  # Minimum daily quote volume (USDT)

    result = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            if symbol not in universe:
                continue

            volume = float(coin["quoteVolume"])

            if volume < MIN_VOLUME:
                continue

            result.append(coin)

        except Exception as e:
            print(f"{symbol}: {e}")

    return result