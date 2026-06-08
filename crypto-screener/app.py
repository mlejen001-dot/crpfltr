import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from market_state import (
    get_market_state
)
from binance_api import (
    get_tickers,
    get_klines_cached
)

from universe_builder import build_universe
from filters import filter_coins

from relative_strength import relative_strength

from indicator import (
    prepare_dataframe,
    ema20,
    ema50,
    rsi,
    volume_spike
)

from scoring import calculate_score


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
    f"BTC 24h Change: {btc_change:.3f}%"
)
print()
print("TOP COINS")
print()

results = []

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

        e20 = ema20(df)

        e50 = ema50(df)

        rsi_value = rsi(df)

        vol_ratio = volume_spike(df)

        change = float(
            coin["priceChangePercent"]
        )

        rs = relative_strength(
            coin,
            btc_change
        )

        base_score = calculate_score(
            change,
            rs,
            e20,
            e50,
            rsi_value,
            vol_ratio
        )

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
            "vol": round(vol_ratio, 2),
            "score": score
        })

    except Exception as e:

        print(
            f"Error {coin['symbol']} : {e}"
        )

results.sort(
    key=lambda x: x["score"],
    reverse=True
)

for item in results[:20]:

    print(
        f"{item['symbol']} "
        f"| 24h={item['change']:.2f}% "
        f"| RS={item['rs']} "
        f"| RSI={item['rsi']} "
        f"| VOL={item['vol']}x "
        f"| SCORE={item['score']}"
    )