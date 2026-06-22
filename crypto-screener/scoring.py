def calculate_score(
    change,
    rs,
    ema20,
    ema50,
    rsi,
    volume_ratio,
    oi_1h,
    oi_4h,
    oi_24h,
    accel
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

    if oi_1h > 3:
        score += 5

    if oi_4h > 5:
        score += 5

    if oi_24h > 10:
        score += 5

    score += accel

    return round(score, 2)