import requests
from cache.cache import (
    cache_is_valid,
    load_cache,
    save_cache
)

BASE_URL = "https://fapi.binance.com"


def get_tickers():

    url = f"{BASE_URL}/fapi/v1/ticker/24hr"

    return requests.get(
        url,
        timeout=10
    ).json()


def get_exchange_info():

    url = f"{BASE_URL}/fapi/v1/exchangeInfo"

    return requests.get(
        url,
        timeout=10
    ).json()


def get_klines(
    symbol,
    interval="4h",
    limit=100
):

    url = (
        f"{BASE_URL}/fapi/v1/klines"
        f"?symbol={symbol}"
        f"&interval={interval}"
        f"&limit={limit}"
    )

    return requests.get(
        url,
        timeout=10
    ).json()


def get_klines_cached(
    symbol,
    interval="4h",
    limit=100
):

    cache_key = (
        f"{symbol}_{interval}"
    )

    if cache_is_valid(cache_key):

        return load_cache(
            cache_key
        )

    data = get_klines(
        symbol,
        interval,
        limit
    )

    save_cache(
        cache_key,
        data
    )

    return data