import json
import os
import time

CACHE_FOLDER = os.path.dirname(__file__)

CACHE_AGE = 300
# 300 detik = 5 menit


def cache_exists(symbol):

    filename = (
        f"{CACHE_FOLDER}/{symbol}.json"
    )

    return os.path.exists(filename)


def cache_is_valid(symbol):

    filename = (
        f"{CACHE_FOLDER}/{symbol}.json"
    )

    if not os.path.exists(filename):
        return False

    age = (
        time.time()
        - os.path.getmtime(filename)
    )

    return age < CACHE_AGE


def load_cache(symbol):

    filename = (
        f"{CACHE_FOLDER}/{symbol}.json"
    )

    with open(
        filename,
        "r"
    ) as f:

        return json.load(f)


def save_cache(
    symbol,
    data
):

    filename = (
        f"{CACHE_FOLDER}/{symbol}.json"
    )

    with open(
        filename,
        "w"
    ) as f:

        json.dump(
            data,
            f
        )