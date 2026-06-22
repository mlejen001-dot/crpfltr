import requests

from cache.cache import (
    cache_is_valid,
    load_cache,
    save_cache
)

BASE_URL = "https://fapi.binance.com"


def fetch_json(url):

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_tickers():

    url = (
        f"{BASE_URL}"
        "/fapi/v1/ticker/24hr"
    )

    return fetch_json(url)


def get_exchange_info():

    url = (
        f"{BASE_URL}"
        "/fapi/v1/exchangeInfo"
    )

    return fetch_json(url)


def get_open_interest(symbol):

    url = (
        f"{BASE_URL}/fapi/v1/openInterest"
        f"?symbol={symbol}"
    )

    return fetch_json(url)


def get_open_interest_hist(
    symbol,
    period="1h",
    limit=30
):

    url = (
        f"{BASE_URL}"
        "/futures/data/openInterestHist"
        f"?symbol={symbol}"
        f"&period={period}"
        f"&limit={limit}"
    )

    return fetch_json(url)


def get_open_interest_hist_cached(
    symbol,
    period="1h",
    limit=30
):

    cache_key = (
        f"OI_{symbol}_{period}"
    )

    if cache_is_valid(cache_key):

        return load_cache(
            cache_key
        )

    data = get_open_interest_hist(
        symbol,
        period,
        limit
    )

    save_cache(
        cache_key,
        data
    )

    return data


def get_klines(
    symbol,
    interval="4h",
    limit=100
):

    url = (
        f"{BASE_URL}"
        "/fapi/v1/klines"
        f"?symbol={symbol}"
        f"&interval={interval}"
        f"&limit={limit}"
    )

    return fetch_json(url)


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