def find_swing_highs(df, left=3, right=3):
    """Return a list of swing highs with index and price."""
    highs = df["high"]
    swing_highs = []

    if len(highs) < left + right + 1:
        return swing_highs

    for i in range(left, len(highs) - right):
        current = highs.iloc[i]
        left_window = highs.iloc[i - left:i]
        right_window = highs.iloc[i + 1:i + 1 + right]

        if current > left_window.max() and current > right_window.max():
            swing_highs.append({
                "index": highs.index[i],
                "price": float(current)
            })

    return swing_highs


def find_swing_lows(df, left=3, right=3):
    """Return a list of swing lows with index and price."""
    lows = df["low"]
    swing_lows = []

    if len(lows) < left + right + 1:
        return swing_lows

    for i in range(left, len(lows) - right):
        current = lows.iloc[i]
        left_window = lows.iloc[i - left:i]
        right_window = lows.iloc[i + 1:i + 1 + right]

        if current < left_window.min() and current < right_window.min():
            swing_lows.append({
                "index": lows.index[i],
                "price": float(current)
            })

    return swing_lows


def last_swing_high(df, left=3, right=3):
    """Return the most recent swing high as (index, price)."""
    swing_highs = find_swing_highs(df, left=left, right=right)
    if not swing_highs:
        return None, None

    latest = swing_highs[-1]
    return latest["index"], latest["price"]


def last_swing_low(df, left=3, right=3):
    """Return the most recent swing low as (index, price)."""
    swing_lows = find_swing_lows(df, left=left, right=right)
    if not swing_lows:
        return None, None

    latest = swing_lows[-1]
    return latest["index"], latest["price"]


def _is_trend_sequence(prices, ascending=True, required=3):
    if len(prices) < required:
        return False

    tail = prices[-required:]
    if ascending:
        return all(tail[i] < tail[i + 1] for i in range(len(tail) - 1))

    return all(tail[i] > tail[i + 1] for i in range(len(tail) - 1))


def _structure_direction(df, left=3, right=3, required=3):
    """Return the prevailing structure direction from recent swing points."""
    swing_highs = find_swing_highs(df, left=left, right=right)
    swing_lows = find_swing_lows(df, left=left, right=right)

    high_prices = [high["price"] for high in swing_highs]
    low_prices = [low["price"] for low in swing_lows]

    if _is_trend_sequence(high_prices, ascending=True, required=required) and _is_trend_sequence(low_prices, ascending=True, required=required):
        return "bullish"

    if _is_trend_sequence(high_prices, ascending=False, required=required) and _is_trend_sequence(low_prices, ascending=False, required=required):
        return "bearish"

    return None


def _structural_extreme(df, structure, left=3, right=3):
    if structure == "bullish":
        return last_swing_low(df, left=left, right=right)[1]
    if structure == "bearish":
        return last_swing_high(df, left=left, right=right)[1]

    return None


def detect_choch(df, left=3, right=3):
    """Detect change of character (CHOCH) based on the structural swing extreme."""
    if len(df) < left + right + 12:
        return False, None, ""

    structure = _structure_direction(df, left=left, right=right, required=3)
    if structure is None:
        return False, None, ""

    pivot = _structural_extreme(df, structure, left=left, right=right)
    if pivot is None:
        return False, None, ""

    close = float(df["close"].iloc[-1])
    if structure == "bearish" and close > pivot:
        return True, round(pivot, 8), "↑"

    if structure == "bullish" and close < pivot:
        return True, round(pivot, 8), "↓"

    return False, None, ""


def detect_bos(df, left=3, right=3):
    """Detect break of structure (BOS) after the current trend is established."""
    if len(df) < left + right + 12:
        return False, None, ""

    structure = _structure_direction(df, left=left, right=right, required=3)
    if structure is None:
        return False, None, ""

    close = float(df["close"].iloc[-1])
    high_pivot = last_swing_high(df, left=left, right=right)[1]
    low_pivot = last_swing_low(df, left=left, right=right)[1]

    if structure == "bullish" and high_pivot is not None and close > high_pivot:
        return True, round(high_pivot, 8), "↑"

    if structure == "bearish" and low_pivot is not None and close < low_pivot:
        return True, round(low_pivot, 8), "↓"

    return False, None, ""
