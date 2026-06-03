def relative_strength(coin, btc_change):

    coin_change = float(coin["priceChangePercent"])

    rs = coin_change - btc_change

    return round(rs, 2)