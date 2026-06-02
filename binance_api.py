import requests

def get_tickers():

    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"

    response = requests.get(url)

    return response.json()