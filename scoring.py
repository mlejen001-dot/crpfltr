def get_btc_change(data):

    for coin in data:

        if coin["symbol"] == "BTCUSDT":

            return float(
                coin["priceChangePercent"]
            )

    return 0
def calculate_score(
    coin,
    btc_change
):

    score = 0

    change = float(
        coin["priceChangePercent"]
    )

    volume = float(
        coin["quoteVolume"]
    )

    # Relative Strength
    rs = change - btc_change

    score += rs

    # Bonus volume

    if volume > 50_000_000:
        score += 5

    if volume > 100_000_000:
        score += 5

    return round(score, 2)