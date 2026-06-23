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

    # Relative Strength
    score += rs

    # Trend
    if ema20 > ema50:
        score += 10

    # RSI
    if 55 <= rsi <= 70:
        score += 10

    elif 70 < rsi <= 80:
        score += 5

    elif rsi > 80:
        score -= 5

    # Volume
    if volume_ratio > 2:
        score += 10

    elif volume_ratio > 1:
        score += 5

    # Open Interest
    if oi_1h > 0:
        score += 2

    if oi_4h > 0:
        score += 3

    if oi_24h > 0:
        score += 5

    if oi_1h < 0:
        score -= 2

    if oi_4h < 0:
        score -= 3

    # Price Change
    if change > 0:
        score += 5

    return round(score, 2)