import requests

def get_tickers():

    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd"
        "&order=market_cap_desc"
        "&per_page=20"
        "&page=1"
        "&sparkline=false"
    )

    response = requests.get(url)

    return response.json()