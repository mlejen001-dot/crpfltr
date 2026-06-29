import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import sys

from binance_api import get_tickers, get_klines_cached
from flow import flow_state
from indicator import (
    prepare_dataframe,
    ema20,
    ema50,
    rsi,
    volume_spike,
)
from market_classifier import classify_coin
from market_state import get_market_state
from market_structure import detect_choch, detect_bos
from btc_regime import btc_regime
from momentum import (
    price_change_1h,
    price_change_4h,
    price_change_24h,
    acceleration_score,
    momentum_state,
)
from oi import oi_change_1h, oi_change_4h, oi_change_24h
from relative_strength import relative_strength
from scoring import calculate_score


def download_ticker(symbol):
    tickers = get_tickers()
    ticker = next((item for item in tickers if item["symbol"] == symbol), None)
    btc = next((item for item in tickers if item["symbol"] == "BTCUSDT"), None)

    if ticker is None:
        raise ValueError(f"Ticker not found: {symbol}")
    if btc is None:
        raise ValueError("BTCUSDT ticker not found")

    return ticker, float(btc["priceChangePercent"])


def download_4h_candles(symbol, limit=100):
    klines = get_klines_cached(symbol, interval="4h", limit=limit)
    return prepare_dataframe(klines)


def compute_indicator_values(symbol, ticker, btc_change, df):
    e20 = ema20(df)
    e50 = ema50(df)
    rsi_value = rsi(df)
    volume_ratio = volume_spike(df)

    rs = relative_strength(ticker, btc_change)

    oi1 = oi_change_1h(symbol)
    oi4 = oi_change_4h(symbol)
    oi24 = oi_change_24h(symbol)

    p1 = price_change_1h(symbol)
    p4 = price_change_4h(symbol)
    p24 = price_change_24h(symbol)

    accel = acceleration_score(p24, p4, p1)
    momentum = momentum_state(p24, p4, p1)
    flow = flow_state(p1, oi1)
    choch, choch_price, choch_dir = detect_choch(df)
    bos, bos_price, bos_dir = detect_bos(df)

    change = float(ticker.get("priceChangePercent", 0))
    price = float(ticker.get("lastPrice", 0))

    distance_choch = None
    if choch_price is not None and choch_price != 0:
        distance_choch = round(((price - choch_price) / choch_price) * 100, 2)

    distance_bos = None
    if bos_price is not None and bos_price != 0:
        distance_bos = round(((price - bos_price) / bos_price) * 100, 2)

    base_score = calculate_score(
        change,
        rs,
        e20,
        e50,
        rsi_value,
        volume_ratio,
        oi1,
        oi4,
        oi24,
        accel,
    )

    bonus = 0
    bonus_reasons = []

    if choch:
        bonus += 5
        bonus_reasons.append("CHOCH detected")
    if bos:
        bonus += 8
        bonus_reasons.append("BOS detected")

    if momentum == "ACCELERATING":
        bonus += 5
        bonus_reasons.append("Momentum accelerating")
    elif momentum == "UPTREND":
        bonus += 3
        bonus_reasons.append("Momentum in uptrend")
    elif momentum == "REVERSAL":
        bonus += 6
        bonus_reasons.append("Reversal momentum")
    elif momentum == "EXHAUSTION":
        bonus -= 5
        bonus_reasons.append("Momentum exhaustion")
    elif momentum == "DOWNTREND":
        bonus -= 10
        bonus_reasons.append("Downtrend momentum")

    if flow == "LONG_BUILD":
        flow_bonus = min(oi4, 10)
        bonus += flow_bonus
        bonus_reasons.append(f"Flow LONG_BUILD (+{flow_bonus:.2f})")
    elif flow == "SHORT_COVER":
        bonus += 3
        bonus_reasons.append("Flow SHORT_COVER")
    elif flow == "SHORT_BUILD":
        bonus -= 5
        bonus_reasons.append("Flow SHORT_BUILD")
    elif flow == "LONG_LIQUIDATION":
        bonus -= 8
        bonus_reasons.append("Flow LONG_LIQUIDATION")

    intermediate_score = round(base_score + bonus, 2)
    market = get_market_state()
    regime = btc_regime()

    final_score = intermediate_score * market["multiplier"]
    if regime == "RISK_ON":
        final_score *= 1.1
    elif regime == "RISK_OFF":
        final_score *= 0.8
    final_score = round(final_score, 2)

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
        p4,
    )

    pros, cons, reasons = build_reasons(
        e20,
        e50,
        rsi_value,
        volume_ratio,
        oi1,
        oi4,
        oi24,
        p1,
        p4,
        p24,
        accel,
        momentum,
        flow,
        choch,
        bos,
        category,
        bonus_reasons,
    )

    setup_quality = score_to_setup(final_score, volume_ratio)
    bias = (
        "Bullish"
        if e20 > e50 and rs > 0
        else "Bearish"
        if e20 < e50 and rs < 0
        else "Neutral"
    )

    action_plan = build_action_plan(
        {
            "price": price,
            "choch": choch,
            "choch_price": choch_price,
            "bos": bos,
            "bos_price": bos_price,
            "distance_choch": distance_choch,
            "distance_bos": distance_bos,
            "score": final_score,
            "bias": bias,
            "category": category,
            "flow": flow,
            "volume_ratio": volume_ratio,
        }
    )

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "rs": rs,
        "ema20": round(e20, 4),
        "ema50": round(e50, 4),
        "rsi": rsi_value,
        "volume_ratio": round(volume_ratio, 2),
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
        "choch_price": choch_price,
        "choch_dir": choch_dir,
        "distance_choch": distance_choch,
        "bos": bos,
        "bos_price": bos_price,
        "bos_dir": bos_dir,
        "distance_bos": distance_bos,
        "base_score": base_score,
        "bonus": bonus,
        "intermediate_score": intermediate_score,
        "market_state": market["state"],
        "multiplier": market["multiplier"],
        "btc_regime": regime,
        "score": final_score,
        "category": category,
        "pros": pros,
        "cons": cons,
        "reasons": reasons,
        "setup_quality": setup_quality,
        "action_plan": action_plan,
    }


def build_reasons(
    e20,
    e50,
    rsi_value,
    volume_ratio,
    oi1,
    oi4,
    oi24,
    p1,
    p4,
    p24,
    accel,
    momentum,
    flow,
    choch,
    bos,
    category,
    bonus_reasons,
):
    pros = []
    cons = []
    reasons = []

    if e20 > e50:
        pros.append("EMA20 above EMA50")
        reasons.append("EMA20 above EMA50 -> bullish trend")
    else:
        cons.append("EMA20 below EMA50")
        reasons.append("EMA20 below EMA50 -> bearish or flat trend")

    if 55 <= rsi_value <= 70:
        pros.append("RSI in healthy bullish range")
        reasons.append("RSI in healthy bullish range")
    elif 70 < rsi_value <= 80:
        reasons.append("RSI high but not extreme")
    elif rsi_value > 80:
        cons.append("RSI overbought")
        reasons.append("RSI overbought")
    elif rsi_value < 30:
        pros.append("RSI oversold")
        reasons.append("RSI oversold")
    else:
        reasons.append("RSI neutral")

    if volume_ratio > 2:
        pros.append("Volume above average")
        reasons.append("Volume ratio strong: current volume is more than double the recent average")
    elif volume_ratio > 1:
        pros.append("Volume above average")
        reasons.append("Volume ratio positive: current volume above average")
    else:
        cons.append("Volume below average")
        reasons.append("Volume ratio weak or neutral")

    if oi1 > 0:
        pros.append("OI 1H rising")
        reasons.append("Open interest 1H rising")
    elif oi1 < 0:
        cons.append("OI 1H falling")
        reasons.append("Open interest 1H falling")
    else:
        reasons.append("Open interest 1H flat")

    if oi4 > 0:
        pros.append("OI 4H rising")
        reasons.append("Open interest 4H rising")
    elif oi4 < 0:
        cons.append("OI 4H falling")
        reasons.append("Open interest 4H falling")
    else:
        reasons.append("Open interest 4H flat")

    if oi24 > 0:
        pros.append("OI 24H rising")
        reasons.append("Open interest 24H rising")
    elif oi24 < 0:
        cons.append("OI 24H falling")
        reasons.append("Open interest 24H falling")
    else:
        reasons.append("Open interest 24H flat")

    if p24 > 0:
        pros.append("Price positive 24H")
        reasons.append("Price 24H positive")
    else:
        cons.append("Price negative or flat 24H")
        reasons.append("Price 24H negative or flat")

    if p4 > 0:
        pros.append("Price positive 4H")
        reasons.append("Price 4H positive")
    else:
        cons.append("Price negative or flat 4H")
        reasons.append("Price 4H negative or flat")

    if p1 > 0:
        pros.append("Price positive 1H")
        reasons.append("Price 1H positive")
    else:
        cons.append("Price negative or flat 1H")
        reasons.append("Price 1H negative or flat")

    reasons.append(f"Acceleration score: {accel:.2f}")
    reasons.append(f"Momentum state: {momentum}")
    reasons.append(f"Flow state: {flow}")

    reasons.extend(bonus_reasons)

    if bos:
        pros.append("BOS confirmed")
        reasons.append("BOS confirmed")
    if choch:
        pros.append("CHOCH confirmed")
        reasons.append("CHOCH confirmed")

    if flow == "LONG_BUILD":
        reasons.append("Long build detected")
    elif flow == "SHORT_COVER":
        reasons.append("Short cover detected")
    elif flow == "SHORT_BUILD":
        reasons.append("Short build detected")
    elif flow == "LONG_LIQUIDATION":
        reasons.append("Long liquidation detected")
    else:
        reasons.append("Flow neutral or undefined")

    if category == "TREND_LEADER":
        pros.append("Trend leader structure")
        reasons.append(
            "Classifier selected TREND_LEADER: BOS structure with bullish flow and/or strong RS/OI conditions."
        )
    elif category == "REVERSAL":
        pros.append("Reversal structure")
        reasons.append(
            "Classifier selected REVERSAL: CHOCH plus rising short-term open interest."
        )
    elif category == "EARLY_TREND":
        pros.append("Early trend structure")
        reasons.append(
            "Classifier selected EARLY_TREND: rising OI, positive 4H move, and trend-supporting momentum."
        )
    else:
        cons.append("Weak classifier setup")
        reasons.append(
            "Classifier selected IGNORE: the current setup does not meet the defined trend or reversal criteria."
        )

    reasons.append(f"Category: {category}")

    return pros, cons, reasons


def score_to_setup(score, volume_ratio):
    if score > 90:
        setup = "Excellent"
    elif score >= 80:
        setup = "High"
    elif score >= 65:
        setup = "Medium"
    elif score >= 50:
        setup = "Low"
    else:
        setup = "Poor"

    if volume_ratio < 1:
        setup = f"{setup} (volume weak)"

    return setup


def build_action_plan(result):
    if result.get("choch") and result.get("choch_price") is not None:
        entry = "Wait retrace"
        entry_zone = f"{result.get('choch_price'):.8f}"
        invalidation = "Close below CHOCH"
        stop_loss = "Close below CHOCH"
        target = "Previous High"
    elif result.get("bos") and result.get("bos_price") is not None:
        entry = "Consider entry"
        entry_zone = f"{result.get('bos_price'):.8f}"
        invalidation = "Close below BOS"
        stop_loss = "Close below BOS"
        target = "Previous High"
    else:
        entry = "No clear entry"
        entry_zone = "N/A"
        invalidation = "N/A"
        stop_loss = "N/A"
        target = "N/A"

    score = result.get("score", 0)
    risk_reward = f"{max(1.0, min(4.0, round(score / 30, 1)))}R"
    confidence = f"{min(100, max(20, int(score * 0.8)))}%"

    return {
        "bias": result.get("bias", "Neutral"),
        "entry": entry,
        "entry_zone": entry_zone,
        "stop_loss": stop_loss,
        "target": target,
        "invalidation": invalidation,
        "risk_reward": risk_reward,
        "confidence": confidence,
    }


def flow_meaning(flow):
    if flow == "LONG_BUILD":
        return "New long positions entering."
    if flow == "SHORT_COVER":
        return "Short positions are covering."
    if flow == "SHORT_BUILD":
        return "Short positions are building."
    if flow == "LONG_LIQUIDATION":
        return "Long positions are liquidating."
    return "No strong flow bias."


def print_analysis(result, verdict):
    print("\n=== COIN ANALYSIS ===")
    print("\n-- Trend --")
    print(f"EMA20        : {result['ema20']:.4f}")
    print(f"EMA50        : {result['ema50']:.4f}")
    print(f"Trend        : {'bullish' if result['ema20'] > result['ema50'] else 'bearish/neutral'}")
    print(f"RSI          : {result['rsi']:.2f}")
    print(f"Relative Str.: {result['rs']:.2f}")
    print(f"Acceleration : {result['accel']:.2f}")
    print(f"Momentum     : {result['momentum']}")
    print(f"Flow         : {result['flow']}")

    print("\n-- Price --")
    print(f"Price        : {result['price']:.8f}")
    print(f"24H Change   : {result['change']:.2f}%")
    print(f"4H Change    : {result['p4']:.2f}%")
    print(f"1H Change    : {result['p1']:.2f}%")
    print(f"24H Change   : {result['p24']:.2f}%")

    print("\n-- Flow --")
    print(f"Volume Ratio : {result['volume_ratio']:.2f}")
    print(f"OI 1H        : {result['oi1']:.2f}%")
    print(f"OI 4H        : {result['oi4']:.2f}%")
    print(f"OI 24H       : {result['oi24']:.2f}%")
    print(f"Flow Meaning : {verdict['flow_meaning']}")

    print("\n-- Structure --")
    if result.get('choch'):
        choch_str = f"{result.get('choch_dir','')} @{result.get('choch_price')}{' ('+str(result.get('distance_choch'))+'%)' if result.get('distance_choch') is not None else ''}"
    else:
        choch_str = "-"

    if result.get('bos'):
        bos_str = f"{result.get('bos_dir','')} @{result.get('bos_price')}{' ('+str(result.get('distance_bos'))+'%)' if result.get('distance_bos') is not None else ''}"
    else:
        bos_str = "-"

    print(f"CHOCH        : {choch_str}")
    print(f"BOS          : {bos_str}")
    print(f"Category     : {result['category']}")

    print("\n-- Score --")
    print(f"Base Score   : {result['base_score']:.2f}")
    print(f"Bonus        : {result['bonus']:.2f}")
    print(f"Intermediate : {result['intermediate_score']:.2f}")
    print(f"Market State : {result['market_state']}")
    print(f"Multiplier   : {result['multiplier']:.2f}")
    print(f"BTC Regime   : {result['btc_regime']}")
    print(f"Final Score  : {result['score']:.2f}")

    print("\n-- VERDICT --")
    print(f"Bias         : {verdict['bias']}")
    print(f"Setup        : {verdict['setup']}")
    print(f"Structure    : {verdict['structure']}")
    print(f"Phase        : {verdict['phase']}")
    print(f"Decision     : {verdict['decision']}")
    print(f"Reason       : {verdict['reason']}")

    print("\n-- PROS / CONS --")
    if result.get('pros'):
        print("Pros:")
        for item in result['pros']:
            print(f"✓ {item}")
    if result.get('cons'):
        print("Cons:")
        for item in result['cons']:
            print(f"✗ {item}")

    print("\n=== ACTION PLAN ===")
    plan = result.get('action_plan', {})
    print(f"Bias         : {plan.get('bias')}")
    print(f"Entry        : {plan.get('entry')}")
    print(f"Entry Zone   : {plan.get('entry_zone')}")
    print(f"Stop Loss    : {plan.get('stop_loss')}")
    print(f"Invalidation : {plan.get('invalidation')}")
    print(f"Target       : {plan.get('target')}")
    print(f"Risk Reward  : {plan.get('risk_reward')}")
    print(f"Confidence   : {plan.get('confidence')}")

    print("\nReasons:")
    for reason in result['reasons']:
        print(f"- {reason}")


def compute_verdict(result):
    if result.get("bos"):
        structure = "BOS"
        distance = result.get("distance_bos")
    elif result.get("choch"):
        structure = "CHOCH"
        distance = result.get("distance_choch")
    else:
        structure = None
        distance = None

    if distance is None:
        phase = "No structure"
    elif abs(distance) <= 5:
        phase = "fresh"
    elif abs(distance) <= 12:
        phase = "extended"
    elif abs(distance) <= 20:
        phase = "late"
    else:
        phase = "too late"

    if result["ema20"] > result["ema50"] and result["rs"] > 0:
        bias = "Bullish"
    elif result["ema20"] < result["ema50"] and result["rs"] < 0:
        bias = "Bearish"
    else:
        bias = "Neutral"

    setup = result.get("setup_quality")
    if not setup:
        setup = score_to_setup(result.get("score", 0), result.get("volume_ratio", 0))

    if (
        structure == "BOS"
        and result["flow"] == "LONG_BUILD"
        and (
            setup.startswith("High")
            or setup.startswith("Excellent")
        )
    ):
        decision = "Enter now"
        reason = "Strong BOS structure with long bias and supportive flow."
    elif structure == "BOS" and result["flow"] == "SHORT_COVER":
        decision = "Cautious"
        reason = "BOS with short cover flow; watch for stabilization."
    elif structure == "CHOCH" and phase == "fresh":
        decision = "Wait for retrace"
        reason = "CHOCH detected; fresh structure, prefer a small pullback."
    elif structure == "CHOCH" and phase == "extended":
        decision = "Consider entry"
        reason = "CHOCH structure is extended but still within reasonable range."
    elif structure == "CHOCH" and phase == "late":
        decision = "Late"
        reason = "CHOCH is already late; risk of entering at the end of the move."
    elif structure == "CHOCH" and phase == "too late":
        decision = "Too late"
        reason = "Price has moved too far from the CHOCH pivot."
    else:
        decision = "Ignore"
        reason = "No clear BOS or CHOCH structure to support an entry."

    return {
        "bias": bias,
        "setup": setup,
        "structure": structure or "None",
        "phase": phase,
        "decision": decision,
        "reason": reason,
        "flow_meaning": flow_meaning(result.get("flow")),
    }


def analyze_coin(symbol):
    ticker, btc_change = download_ticker(symbol)
    df = download_4h_candles(symbol)
    return compute_indicator_values(symbol, ticker, btc_change, df)


def main():
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = input("Masukkan ticker (contoh BTCUSDT): ").strip().upper()

    if not symbol:
        print("Symbol tidak boleh kosong")
        return

    try:
        result = analyze_coin(symbol)
        verdict = compute_verdict(result)
        print_analysis(result, verdict)
    except Exception as error:
        print(f"Gagal menganalisa {symbol}: {error}")


if __name__ == "__main__":
    main()
