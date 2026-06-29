def find_pivots(df, left=3, right=3):
    """Return a list of swing pivots with type (High/Low) and price."""
    pivots = []
    if len(df) < max(3, left + right + 1):
        return pivots

    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()

    for i in range(left, len(df) - right):
        current_high = float(highs[i])
        current_low = float(lows[i])
        left_high_window = highs[max(0, i - left):i]
        right_high_window = highs[i + 1:i + 1 + right]
        left_low_window = lows[max(0, i - left):i]
        right_low_window = lows[i + 1:i + 1 + right]

        left_high_max = left_high_window.max() if len(left_high_window) else float("-inf")
        right_high_max = right_high_window.max() if len(right_high_window) else float("-inf")
        left_low_min = left_low_window.min() if len(left_low_window) else float("inf")
        right_low_min = right_low_window.min() if len(right_low_window) else float("inf")

        is_high_pivot = current_high >= left_high_max and current_high > right_high_max
        is_low_pivot = current_low <= left_low_min and current_low < right_low_min

        if is_high_pivot:
            pivots.append({"index": df.index[i], "price": current_high, "type": "High"})
        if is_low_pivot:
            pivots.append({"index": df.index[i], "price": current_low, "type": "Low"})

    return sorted(pivots, key=lambda item: item["index"])


def merge_pivots(pivots, tolerance_ratio=0.002):
    """Merge repeated pivots that are too close in price to reduce noise."""
    if not pivots:
        return []

    merged = []
    for pivot in sorted(pivots, key=lambda item: item["index"]):
        if not merged:
            merged.append(pivot)
            continue

        prev = merged[-1]
        if prev["type"] == pivot["type"]:
            prev_price = abs(prev["price"])
            if prev_price <= 0:
                prev_price = 1.0
            if abs(pivot["price"] - prev["price"]) / prev_price <= tolerance_ratio:
                if pivot["index"] > prev["index"]:
                    merged[-1] = pivot
                continue

        merged.append(pivot)

    return merged


def classify_swings(pivots):
    """Assign swing labels such as HH, HL, LH, LL to pivots."""
    classified = []
    last_high = None
    last_low = None

    for pivot in pivots:
        if pivot["type"] == "High":
            label = None
            direction = "up"
            if last_high is not None:
                label = "HH" if pivot["price"] > last_high["price"] else "LH"
                direction = "up" if label == "HH" else "down"
            last_high = pivot
        else:
            label = None
            direction = "up"
            if last_low is not None:
                label = "HL" if pivot["price"] > last_low["price"] else "LL"
                direction = "up" if label == "HL" else "down"
            last_low = pivot

        classified.append({
            "index": pivot["index"],
            "price": pivot["price"],
            "type": pivot["type"],
            "label": label,
            "direction": direction,
        })

    return classified


def find_swing_highs(df, left=3, right=3):
    """Return a list of swing highs with index and price."""
    return [
        {"index": pivot["index"], "price": pivot["price"]}
        for pivot in find_pivots(df, left=left, right=right)
        if pivot["type"] == "High"
    ]


def find_swing_lows(df, left=3, right=3):
    """Return a list of swing lows with index and price."""
    return [
        {"index": pivot["index"], "price": pivot["price"]}
        for pivot in find_pivots(df, left=left, right=right)
        if pivot["type"] == "Low"
    ]


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


def detect_market_trend(df, left=3, right=3):
    """Return the dominant market structure trend: bullish, bearish, or neutral."""
    pivots = merge_pivots(find_pivots(df, left=left, right=right))
    classified = classify_swings(pivots)

    high_pivots = [pivot for pivot in classified if pivot["type"] == "High" and pivot["label"] is not None]
    low_pivots = [pivot for pivot in classified if pivot["type"] == "Low" and pivot["label"] is not None]

    if len(high_pivots) >= 3 and len(low_pivots) >= 3:
        recent_high_labels = [pivot["label"] for pivot in high_pivots[-3:]]
        recent_low_labels = [pivot["label"] for pivot in low_pivots[-3:]]
        if recent_high_labels == ["HH", "HH", "HH"] and recent_low_labels == ["HL", "HL", "HL"]:
            return "bullish"
        if recent_high_labels == ["LH", "LH", "LH"] and recent_low_labels == ["LL", "LL", "LL"]:
            return "bearish"

    return "neutral"


def detect_inducement(df, left=3, right=3):
    """Detect a liquidity sweep or induced move around the latest structural extreme."""
    if len(df) < 2:
        return False, None, ""

    prev_df = df.iloc[:-1]
    pivots = merge_pivots(find_pivots(prev_df, left=left, right=right))
    if pivots:
        last_high_pivot = max((pivot for pivot in pivots if pivot["type"] == "High"), key=lambda pivot: pivot["index"], default=None)
        last_low_pivot = max((pivot for pivot in pivots if pivot["type"] == "Low"), key=lambda pivot: pivot["index"], default=None)
    else:
        last_high_pivot = {"price": float(prev_df["high"].iloc[-1])} if len(prev_df) >= 1 else None
        last_low_pivot = {"price": float(prev_df["low"].iloc[-1])} if len(prev_df) >= 1 else None

    current_high = float(df["high"].iloc[-1])
    current_low = float(df["low"].iloc[-1])
    current_close = float(df["close"].iloc[-1])

    if last_high_pivot is not None and current_high > last_high_pivot["price"] and current_close < last_high_pivot["price"]:
        return True, round(last_high_pivot["price"], 8), "sweep"
    if last_low_pivot is not None and current_low < last_low_pivot["price"] and current_close > last_low_pivot["price"]:
        return True, round(last_low_pivot["price"], 8), "sweep"

    return False, None, ""


def detect_choch(df, left=3, right=3):
    """Detect change of character (CHOCH) with better quality filtering."""
    if len(df) < 3:
        return False, None, ""

    prev_df = df.iloc[:-1]
    pivots = merge_pivots(find_pivots(prev_df, left=left, right=right))
    trend = detect_market_trend(prev_df, left=left, right=right)
    close = float(df["close"].iloc[-1])

    if trend == "bullish":
        last_low_pivot = max((pivot for pivot in pivots if pivot["type"] == "Low"), key=lambda pivot: pivot["index"], default=None)
        if last_low_pivot is not None:
            threshold = max(abs(last_low_pivot["price"]) * 0.0005, 1e-6)
            if close < last_low_pivot["price"] and abs(close - last_low_pivot["price"]) >= threshold:
                return True, round(last_low_pivot["price"], 8), "↓"

    if trend == "bearish":
        last_high_pivot = max((pivot for pivot in pivots if pivot["type"] == "High"), key=lambda pivot: pivot["index"], default=None)
        if last_high_pivot is not None:
            threshold = max(abs(last_high_pivot["price"]) * 0.0005, 1e-6)
            if close > last_high_pivot["price"] and abs(close - last_high_pivot["price"]) >= threshold:
                return True, round(last_high_pivot["price"], 8), "↑"

    return False, None, ""


def detect_bos(df, left=3, right=3):
    """Detect break of structure (BOS) after an established trend."""
    if len(df) < 3:
        return False, None, ""

    prev_df = df.iloc[:-1]
    pivots = classify_swings(merge_pivots(find_pivots(prev_df, left=left, right=right)))
    trend = detect_market_trend(prev_df, left=left, right=right)
    close = float(df["close"].iloc[-1])

    if trend == "bullish":
        last_high_pivot = next((pivot for pivot in reversed(pivots) if pivot["type"] == "High" and pivot["label"] == "HH"), None)
        if last_high_pivot is not None:
            threshold = max(abs(last_high_pivot["price"]) * 0.0005, 1e-6)
            if close > last_high_pivot["price"] and abs(close - last_high_pivot["price"]) >= threshold:
                return True, round(last_high_pivot["price"], 8), "↑"

    if trend == "bearish":
        last_low_pivot = next((pivot for pivot in reversed(pivots) if pivot["type"] == "Low" and pivot["label"] == "LL"), None)
        if last_low_pivot is not None:
            threshold = max(abs(last_low_pivot["price"]) * 0.0005, 1e-6)
            if close < last_low_pivot["price"] and abs(close - last_low_pivot["price"]) >= threshold:
                return True, round(last_low_pivot["price"], 8), "↓"

    return False, None, ""


def build_supply_zone(df, pivot=None, left=3, right=3):
    """Build a supply zone from a recent swing high pivot."""
    if pivot is None:
        _, pivot_price = last_swing_high(df, left=left, right=right)
        if pivot_price is None:
            return None
        pivot = {"index": df.index[-1], "price": pivot_price, "type": "High"}

    bar_idx = pivot["index"] if pivot["index"] in df.index else df.index.get_loc(pivot["index"])
    open_price = float(df["open"].iloc[bar_idx]) if "open" in df.columns else float(df["close"].iloc[bar_idx])
    close_price = float(df["close"].iloc[bar_idx])
    return {
        "type": "supply",
        "pivot": float(pivot["price"]),
        "top": float(df["high"].iloc[bar_idx]),
        "bottom": min(open_price, close_price),
        "status": "fresh",
    }


def build_demand_zone(df, pivot=None, left=3, right=3):
    """Build a demand zone from a recent swing low pivot."""
    if pivot is None:
        _, pivot_price = last_swing_low(df, left=left, right=right)
        if pivot_price is None:
            return None
        pivot = {"index": df.index[-1], "price": pivot_price, "type": "Low"}

    bar_idx = pivot["index"] if pivot["index"] in df.index else df.index.get_loc(pivot["index"])
    open_price = float(df["open"].iloc[bar_idx]) if "open" in df.columns else float(df["close"].iloc[bar_idx])
    close_price = float(df["close"].iloc[bar_idx])
    return {
        "type": "demand",
        "pivot": float(pivot["price"]),
        "top": max(open_price, close_price),
        "bottom": float(df["low"].iloc[bar_idx]),
        "status": "fresh",
    }


def update_zone_status(zone, df):
    """Update zone status based on the latest price action relative to the zone."""
    if zone is None:
        return None

    close = float(df["close"].iloc[-1])
    high = float(df["high"].iloc[-1])
    low = float(df["low"].iloc[-1])

    if zone["type"] == "supply":
        if high > zone["top"]:
            zone["status"] = "broken"
        elif zone["bottom"] <= close <= zone["top"]:
            zone["status"] = "mitigated"
        else:
            zone["status"] = "fresh"
    else:
        if low < zone["bottom"]:
            zone["status"] = "broken"
        elif zone["bottom"] <= close <= zone["top"]:
            zone["status"] = "mitigated"
        else:
            zone["status"] = "fresh"
    return zone


def get_latest_structure(df, left=3, right=3):
    """Return a compact summary of the latest market structure state."""
    pivots = merge_pivots(find_pivots(df, left=left, right=right))
    trend = detect_market_trend(df, left=left, right=right)
    choch, choch_price, choch_dir = detect_choch(df, left=left, right=right)
    bos, bos_price, bos_dir = detect_bos(df, left=left, right=right)
    last_high = last_swing_high(df, left=left, right=right)
    last_low = last_swing_low(df, left=left, right=right)

    return {
        "trend": trend,
        "pivots": pivots,
        "last_high": last_high,
        "last_low": last_low,
        "choch": choch,
        "choch_price": choch_price,
        "choch_dir": choch_dir,
        "bos": bos,
        "bos_price": bos_price,
        "bos_dir": bos_dir,
    }


def structure_phase(df, left=3, right=3):
    """Return a structure phase label aligned with market structure states."""
    structure = get_latest_structure(df, left=left, right=right)
    trend = structure["trend"]

    if trend == "bullish":
        if structure["bos"]:
            return "Bull BOS"
        if structure["choch"]:
            return "Bull CHOCH"
        return "Bull Trend"
    if trend == "bearish":
        if structure["bos"]:
            return "Bear BOS"
        if structure["choch"]:
            return "Bear CHOCH"
        return "Bear Trend"
    return "Range"
