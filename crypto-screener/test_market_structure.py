import pandas as pd

from market_structure import (
    build_demand_zone,
    build_supply_zone,
    classify_swings,
    detect_bos,
    detect_choch,
    detect_inducement,
    detect_market_trend,
    find_pivots,
    structure_phase,
    update_zone_status,
)


def test_find_pivots_and_classify_swings():
    df = pd.DataFrame(
        {
            "high": [10, 8, 9, 7, 8, 6, 7, 5, 6, 4, 7],
            "low": [4, 3, 4, 2, 3, 1, 2, 0, 1, -1, 2],
            "close": [7, 6, 7, 5, 6, 4, 5, 3, 4, 2, 5],
        }
    )

    pivots = find_pivots(df, left=1, right=1)
    assert pivots

    classified = classify_swings(pivots)
    labels = {item["type"] + item["direction"] for item in classified}
    assert labels


def test_detect_choch_and_bos_on_simple_structure():
    df = pd.DataFrame(
        {
            "high": [10, 9, 11, 10, 12, 11, 13, 12, 14, 13, 13],
            "low": [4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 4],
            "close": [8, 7, 9, 8, 10, 9, 11, 10, 13, 12, 6],
        }
    )

    choch, choch_price, choch_dir = detect_choch(df, left=1, right=1)
    assert choch is True
    assert choch_price is not None

    bos_df = pd.DataFrame(
        {
            "high": [10, 9, 11, 10, 12, 11, 13, 12, 14, 13, 15],
            "low": [4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9],
            "close": [8, 7, 9, 8, 10, 9, 11, 10, 13, 12, 14],
        }
    )
    bos, bos_price, bos_dir = detect_bos(bos_df, left=1, right=1)
    assert bos is True
    assert bos_price is not None


def test_detect_market_trend_requires_three_higher_highs_and_higher_lows():
    df = pd.DataFrame(
        {
            "high": [10, 11, 12, 13],
            "low": [4, 5, 6, 7],
            "close": [7, 8, 9, 10],
        }
    )

    assert detect_market_trend(df, left=1, right=1) == "neutral"


def test_detect_inducement_uses_prior_pivot_not_latest_candle():
    df = pd.DataFrame(
        {
            "high": [10, 11, 10, 12],
            "low": [4, 5, 4, 6],
            "close": [8, 9, 7, 10],
        }
    )

    swept, price, label = detect_inducement(df, left=1, right=1)
    assert swept is True
    assert price == 11
    assert label == "sweep"


def test_detect_choch_and_bos_use_close_for_confirmation():
    choch_df = pd.DataFrame(
        {
            "high": [10, 9, 11, 10, 12, 11, 13, 12, 14, 13, 13],
            "low": [4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 4],
            "close": [8, 7, 9, 8, 10, 9, 11, 10, 13, 12, 6],
        }
    )

    choch, choch_price, choch_dir = detect_choch(choch_df, left=1, right=1)
    assert choch is True
    assert choch_price is not None

    bos_df = pd.DataFrame(
        {
            "high": [10, 9, 11, 10, 12, 11, 13, 12, 14, 13, 15],
            "low": [4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9],
            "close": [8, 7, 9, 8, 10, 9, 11, 10, 13, 12, 14],
        }
    )

    bos, bos_price, bos_dir = detect_bos(bos_df, left=1, right=1)
    assert bos is True
    assert bos_price is not None


def test_zone_building_and_status_logic():
    df = pd.DataFrame(
        {
            "open": [8, 9, 10],
            "high": [10, 11, 12],
            "low": [6, 7, 8],
            "close": [7, 8, 9],
        }
    )

    supply_zone = build_supply_zone(df, pivot={"index": 1, "price": 11, "type": "High"})
    demand_zone = build_demand_zone(df, pivot={"index": 1, "price": 7, "type": "Low"})

    assert supply_zone["top"] == 11
    assert supply_zone["bottom"] == 8
    assert demand_zone["top"] == 9
    assert demand_zone["bottom"] == 7

    updated_supply = update_zone_status(supply_zone, df)
    updated_demand = update_zone_status(demand_zone, df)

    assert updated_supply["status"] == "broken"
    assert updated_demand["status"] == "mitigated"


def test_structure_phase_follows_structure_state():
    df = pd.DataFrame(
        {
            "high": [10, 9, 11, 10, 12, 11, 13, 12, 14, 13, 15],
            "low": [4, 3, 5, 4, 6, 5, 7, 6, 8, 7, 9],
            "close": [8, 7, 9, 8, 10, 9, 11, 10, 13, 12, 14],
        }
    )

    assert structure_phase(df, left=1, right=1) == "Bull Trend"
