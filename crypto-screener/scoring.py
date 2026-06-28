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

    # =====================
    # STRENGTH
    # =====================

    score += rs * 0.5

    # =====================
    # OI LEADING SIGNAL
    # =====================

    score += oi_1h * 1

    score += oi_4h * 5

    score += oi_24h * 1

    # =====================
    # MOMENTUM
    # =====================

    score += accel * 0.5

    # =====================
    # TREND
    # =====================

    if ema20 > ema50:
        score += 10

    # =====================
    # RSI
    # =====================

    if 55 <= rsi <= 70:
        score += 10

    elif 70 < rsi <= 80:
        score += 5

    elif rsi > 80:
        score -= 5

    # =====================
    # VOLUME
    # =====================

    if volume_ratio > 2:
        score += 10

    elif volume_ratio > 1:
        score += 5

    # =====================
    # OI BONUS
    # =====================

    if oi_1h > 0:
        score += 2

    if oi_4h > 0:
        score += 3

    if oi_24h > 0:
        score += 5

    # =====================
    # OI NEGATIVE
    # =====================

    if oi_1h < 0:
        score -= 2

    if oi_4h < 0:
        score -= 3

    # =====================
    # PRICE
    # =====================

    if change > 0:
        score += 5

    return round(
        score,
        2
    )