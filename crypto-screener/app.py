import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

from market_state import (
    get_market_state
)

from binance_api import (
    get_tickers,
    get_klines_cached
)

from universe_builder import (
    build_universe
)

from filters import (
    filter_coins
)

from relative_strength import (
    relative_strength
)

from indicator import (
    prepare_dataframe,
    ema20,
    ema50,
    rsi,
    volume_spike
)

from momentum import (
    price_change_1h,
    price_change_4h,
    price_change_24h,
    acceleration_score,
    momentum_state
)

from oi import (
    oi_change_1h,
    oi_change_4h,
    oi_change_24h
)

from flow import (
    flow_state
)

from scoring import (
    calculate_score
)

from market_classifier import (
    classify_coin
)

# ====================================
# LOAD DATA
# ====================================

data = get_tickers()

universe = build_universe()

filtered = filter_coins(
    data,
    universe
)

btc = next(
    x for x in data
    if x["symbol"] == "BTCUSDT"
)

btc_change = float(
    btc["priceChangePercent"]
)

market = get_market_state()

print()
print(
    f"Market State : {market['state']}"
)

print(
    f"Multiplier : {market['multiplier']}"
)

print()
print(
    f"BTC 24h Change : {btc_change:.2f}%"
)

print()

results = []

# ====================================
# MAIN LOOP
# ====================================

for coin in filtered:

    try:

        symbol = coin["symbol"]

        klines = get_klines_cached(
            symbol,
            interval="4h",
            limit=100
        )

        df = prepare_dataframe(
            klines
        )

        # ==========================
        # TECHNICAL
        # ==========================

        e20 = ema20(df)

        e50 = ema50(df)

        rsi_value = rsi(df)

        vol_ratio = volume_spike(df)

        # ==========================
        # PRICE
        # ==========================

        change = float(
            coin["priceChangePercent"]
        )

        rs = relative_strength(
            coin,
            btc_change
        )

        # ==========================
        # OPEN INTEREST
        # ==========================

        oi1 = oi_change_1h(
            symbol
        )

        oi4 = oi_change_4h(
            symbol
        )

        oi24 = oi_change_24h(
            symbol
        )

        # ==========================
        # MOMENTUM
        # ==========================

        p1 = price_change_1h(
            symbol
        )

        p4 = price_change_4h(
            symbol
        )

        p24 = price_change_24h(
            symbol
        )

        accel = acceleration_score(
            p24,
            p4,
            p1
        )

        momentum = momentum_state(
            p24,
            p4,
            p1
        )

        # ==========================
        # FLOW
        # ==========================

        flow = flow_state(
            p1,
            oi1
        )

        # ==========================
        # CATEGORY
        # ==========================

        category = classify_coin(
            rs,
            rsi_value,
            oi1,
            oi4,
            accel,
            momentum,
            flow
        )

        # ==========================
        # SCORE
        # ==========================

        base_score = calculate_score(
            change,
            rs,
            e20,
            e50,
            rsi_value,
            vol_ratio,
            oi1,
            oi4,
            oi24,
            accel
        )

        # ==========================
        # MOMENTUM BONUS
        # ==========================

        if momentum == "ACCELERATING":

            base_score += 5

        elif momentum == "UPTREND":

            base_score += 3

        elif momentum == "REVERSAL":

            base_score += 6

        elif momentum == "EXHAUSTION":

            base_score -= 5

        elif momentum == "DOWNTREND":

            base_score -= 10

        # ==========================
        # FLOW BONUS
        # ==========================

        if flow == "LONG_BUILD":

            base_score += 5

        elif flow == "SHORT_COVER":

            base_score += 3

        elif flow == "SHORT_BUILD":

            base_score -= 5

        elif flow == "LONG_LIQUIDATION":

            base_score -= 8

        # ==========================
        # MARKET MULTIPLIER
        # ==========================

        score = round(
            base_score *
            market["multiplier"],
            2
        )

        results.append({

            "symbol": symbol,

            "change": change,

            "rs": rs,

            "rsi": rsi_value,

            "vol": round(
                vol_ratio,
                2
            ),

            "oi1": oi1,

            "oi4": oi4,

            "oi24": oi24,

            "accel": accel,

            "momentum": momentum,

            "flow": flow,

            "category": category,

            "score": score

        })

    except Exception as e:

        print(
            f"Error {symbol}: {e}"
        )

# ====================================
# GROUPING
# ====================================

leaders = [
    x for x in results
    if x["category"] == "TREND_LEADER"
]

early = [
    x for x in results
    if x["category"] == "EARLY_TREND"
]

reversal = [
    x for x in results
    if x["category"] == "REVERSAL"
]

# ====================================
# SORT
# ====================================

leaders.sort(
    key=lambda x: x["score"],
    reverse=True
)

early.sort(
    key=lambda x: x["oi24"],
    reverse=True
)

reversal.sort(
    key=lambda x: x["accel"],
    reverse=True
)

# ====================================
# OUTPUT
# ====================================

print("\nTREND LEADERS\n")

for item in leaders[:10]:

    print(
        f"{item['symbol']:<12}"
        f"| SCORE={item['score']:>7.2f}"
        f" | RS={item['rs']:>6.2f}"
        f" | OI24={item['oi24']:>6.2f}%"
        f" | {item['flow']}"
    )

print("\nEARLY TREND\n")

for item in early[:10]:

    print(
        f"{item['symbol']:<12}"
        f"| OI24={item['oi24']:>6.2f}%"
        f" | ACC={item['accel']:>7.2f}"
        f" | {item['flow']}"
    )

print("\nREVERSAL CANDIDATES\n")

for item in reversal[:10]:

    print(
        f"{item['symbol']:<12}"
        f"| ACC={item['accel']:>7.2f}"
        f" | OI1={item['oi1']:>6.2f}%"
        f" | {item['flow']}"
    )