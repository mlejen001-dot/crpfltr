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

from btc_regime import (
    btc_regime
)
from market_structure import (
    detect_choch,
    detect_bos
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

btc_state = btc_regime()

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

print(
    f"BTC Regime : {btc_state}"
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
        choch, choch_price, choch_dir = detect_choch(df)

        bos, bos_price, bos_dir = detect_bos(df)
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
        price = float(
            coin["lastPrice"]
        )

        distance_choch = None
        if choch_price:
            distance_choch = round(
                ((price - choch_price) / choch_price) * 100,
                2
            )

        distance_bos = None
        if bos_price:
            distance_bos = round(
                ((price - bos_price) / bos_price) * 100,
                2
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
        # BASE SCORE
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
        # SCORE
        # ==========================
        if choch:
            base_score += 5
        if bos:
            base_score += 8
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

        if flow=="LONG_BUILD":

            base_score += min(
                oi4,
                10
            )

        elif flow == "SHORT_COVER":

            base_score += 3

        elif flow == "SHORT_BUILD":

            base_score -= 5

        elif flow == "LONG_LIQUIDATION":

            base_score -= 8

        # ==========================
        # MARKET REGIME
        # ==========================

        score = (
            base_score *
            market["multiplier"]
        )

        if btc_state == "RISK_ON":

            score *= 1.1

        elif btc_state == "RISK_OFF":

            score *= 0.8

        score = round(
            score,
            2
        )
        # ==========================
        # CATEGORY
        # ==========================

        category = classify_coin(
            rs,
            oi1,
            oi4,
            oi24,
            accel,
            momentum,
            flow,
            choch,
            bos,
            p4
        )
        results.append({

            "symbol": symbol,

            "price": price,
            
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

            "p1": p1,

            "p4": p4,

            "p24": p24,

            "accel": accel,

            "momentum": momentum,

            "flow": flow,

            "choch": choch,
            "choch_dir": choch_dir,
            
            "choch_price": choch_price,

            "distance_choch": distance_choch,

            "bos": bos,

            "bos_price": bos_price,
            "bos_dir": bos_dir,

            "distance_bos": distance_bos,

            "category": category,

            "score": score

        })

    except Exception as e:

        print(symbol,e)

        continue
    


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
# SORTING
# ====================================

leaders.sort(
    key=lambda x: x["score"],
    reverse=True
)

early.sort(
    key=lambda x: (
        x["choch"],
        x["oi4"],
        x["oi1"],
        x["accel"],
        x["p24"],
    ),
    reverse=True
)

reversal.sort(
    key=lambda x: (
        x["choch"],
        x["oi4"],
        x["oi1"],
        x["accel"],
        x["p24"],
    ),
    reverse=True
)
# ====================================
# OUTPUT
# ====================================

print("\nTREND LEADERS\n")

for item in leaders[:10]:

    # --------------------------
    # CHOCH
    # --------------------------
    if item["choch"]:

        if item["distance_choch"] is not None:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']} "
                f"({item['distance_choch']:+.2f}%)"
            )

        else:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']}"
            )

    else:

        choch_str = "CHOCH -"

    # --------------------------
    # BOS
    # --------------------------
    if item["bos"]:

        if item["distance_bos"] is not None:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']} "
                f"({item['distance_bos']:+.2f}%)"
            )

        else:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']}"
            )

    else:

        bos_str = "BOS -"

    print(
        f"{item['symbol']:<12}"
        f"| PRICE={item['price']:>10.6f}"
        f"| p24={item['p24']:>6.2f}%"
        f" | p4={item['p4']:>6.2f}%"
        f" | RS={item['rs']:>6.2f}"
        f" | OI4={item['oi4']:>6.2f}%"
        f" | OI24={item['oi24']:>6.2f}%"
        f" | ACC={item['accel']:>7.2f}"
        f" | {item['flow']}"
        f" | {choch_str}"
        f" | {bos_str}"
    )


print("\nEARLY TREND\n")

for item in early[:15]:

    # --------------------------
    # CHOCH
    # --------------------------
    if item["choch"]:

        if item["distance_choch"] is not None:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']} "
                f"({item['distance_choch']:+.2f}%)"
            )

        else:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']}"
            )

    else:

        choch_str = "CHOCH -"

    # --------------------------
    # BOS
    # --------------------------
    if item["bos"]:

        if item["distance_bos"] is not None:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']} "
                f"({item['distance_bos']:+.2f}%)"
            )

        else:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']}"
            )

    else:

        bos_str = "BOS -"

    print(
        f"{item['symbol']:<12}"
        f"| PRICE={item['price']:>10.6f}"
        f"| p24={item['p24']:>6.2f}%"
        f" | OI4={item['oi4']:>6.2f}%"
        f" | OI1={item['oi1']:>6.2f}%"
        f" | ACC={item['accel']:>7.2f}"
        f" | {choch_str}"
        f" | {bos_str}"
        f" | {item['flow']}"
    )


print("\nREVERSAL CANDIDATES\n")

for item in reversal[:10]:

    # --------------------------
    # CHOCH
    # --------------------------
    if item["choch"]:

        if item["distance_choch"] is not None:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']} "
                f"({item['distance_choch']:+.2f}%)"
            )

        else:

            choch_str = (
                f"CHOCH {item['choch_dir']} "
                f"@{item['choch_price']}"
            )

    else:

        choch_str = "CHOCH -"

    # --------------------------
    # BOS
    # --------------------------
    if item["bos"]:

        if item["distance_bos"] is not None:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']} "
                f"({item['distance_bos']:+.2f}%)"
            )

        else:

            bos_str = (
                f"BOS ↑ "
                f"@{item['bos_price']}"
            )

    else:

        bos_str = "BOS -"

    print(
        f"{item['symbol']:<12}"
        f"| PRICE={item['price']:>10.6f}"
        f"| p24={item['p24']:>6.2f}%"
        f"| ACC={item['accel']:>7.2f}"
        f" | OI1={item['oi1']:>6.2f}%"
        f" | OI4={item['oi4']:>6.2f}%"
        f" | RS={item['rs']:>6.2f}"
        f" | {choch_str}"
        f" | {bos_str}"
        f" | {item['flow']}"
    )
