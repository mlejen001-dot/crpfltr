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
    else:
        score -= 10

    # RSI
    if 55 <= rsi <= 70:
        score += 10

    elif 70 < rsi <= 80:
        score += 5

    elif rsi > 80:
        score -= 10

    elif rsi < 40:
        score -= 5

    # Volume
    if volume_ratio > 1.5:
        score += 10

    elif volume_ratio > 1:
        score += 5

    # OI
    if oi_1h > 3:
        score += 5

    if oi_4h > 5:
        score += 5

    if oi_24h > 10:
        score += 5

    # OI Collapse
    if oi_1h < -3:
        score -= 5

    if oi_4h < -5:
        score -= 5

    # Price
    if change > 0:
        score += 5

    # Momentum contribution
    score += accel * 0.15

    return round(score, 2)