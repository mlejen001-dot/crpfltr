def calculate_score(coin):

    score = float(
        coin["priceChangePercent"]
    )

    return round(score, 2)