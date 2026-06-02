def filter_coins(data):

    result = []

    for coin in data:

        change = coin["price_change_percentage_24h"]

        if change is not None and change > 5:

            result.append(coin)

    return result