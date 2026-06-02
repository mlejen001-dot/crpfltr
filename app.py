from binance_api import get_tickers
from filters import filter_coins
from scoring import (
    calculate_score,
    get_btc_change
)

# ambil data Binance
data = get_tickers()

# cari BTC change
btc_change = get_btc_change(data)

print(
    f"\nBTC 24h Change: {btc_change}%\n"
)

# filter coin
filtered = filter_coins(data)

results = []

for coin in filtered:

    try:

        change = float(
            coin["priceChangePercent"]
        )

        rs = round(
            change - btc_change,
            2
        )

        score = calculate_score(
            coin,
            btc_change
        )

        results.append({
            "symbol": coin["symbol"],
            "change": change,
            "rs": rs,
            "score": score
        })

    except Exception:
        pass

# ranking berdasarkan score
results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print("TOP COINS\n")

for coin in results[:20]:

    print(
        f"{coin['symbol']} | "
        f"24h={coin['change']}% | "
        f"RS={coin['rs']} | "
        f"Score={coin['score']}"
    )