def filter_coins(data, universe):

    result = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            if symbol not in universe:
                continue

            volume = float(coin["quoteVolume"])

            if volume < 20_000_000:
                continue

            result.append(coin)

        except:
            pass

    return result