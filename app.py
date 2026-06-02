from binance_api import get_tickers
from filters import filter_coins

data = get_tickers()

filtered = filter_coins(data)

for coin in filtered:

    print(
        f"{coin['symbol'].upper()} "
        f"{coin['price_change_percentage_24h']:.2f}%"
    )