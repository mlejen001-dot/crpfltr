from binance_api import get_tickers
from filters import filter_coins
from scoring import (
    calculate_score,
    get_btc_change
)

data = get_tickers()

btc_change = get_btc_change(data)

print(
    f"\nBTC 24h Change: {btc_change}%\n"
)

filtered = filter_coins(data)

results = []

for coin in filtered:

    try:

        symbol = coin["symbol"]

        change = float(
            coin["priceChangePercent"]
        )

        volume = float(
            coin["quoteVolume"]
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

            "symbol": symbol,
            "change": change,
            "volume": volume,
            "rs": rs,
            "score": score

        })

    except Exception:
        pass

results = sorted(
    results,
    key=lambda x: x["score"],
    reverse=True
)

print("TOP COINS\n")

for coin in results:

    print(
        f"{coin['symbol']:<12}"
        f"Change={coin['change']:>7.2f}% | "
        f"RS={coin['rs']:>6.2f} | "
        f"Vol=${coin['volume']/1_000_000:>7.1f}M | "
        f"Score={coin['score']:>6.2f}"
    )