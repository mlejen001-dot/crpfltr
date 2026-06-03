def calculate_score(
    change,
    rs,
    ema20,
    ema50,
    rsi,
    volume_ratio
):

    score = 0

    score += rs

    if ema20 > ema50:
        score += 10

    if 55 <= rsi <= 70:
        score += 10

    if volume_ratio > 1.5:
        score += 10

    if change > 0:
        score += 5

    return round(score, 2)