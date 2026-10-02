"""Tests de src/analysis.py."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analysis import (  # noqa: E402
    compute_daily_returns,
    compute_rolling_volatility,
    load_prices,
)


def test_daily_returns_happy_path():
    prices = pd.Series([100.0, 110.0, 99.0])
    returns = compute_daily_returns(prices)

    assert len(returns) == 2
    assert returns.iloc[0] == pytest.approx(0.10)
    assert returns.iloc[1] == pytest.approx(-0.10)


def test_load_sample_data_is_sorted_and_complete():
    df = load_prices()

    assert "Close" in df.columns
    assert df.index.is_monotonic_increasing
    assert df["Close"].notna().all()


def test_rolling_volatility_window_larger_than_data_is_all_nan():
    returns = pd.Series([0.01, -0.02, 0.03])
    vol = compute_rolling_volatility(returns, window=10)

    assert vol.isna().all()


def test_rolling_volatility_rejects_window_below_two():
    with pytest.raises(ValueError):
        compute_rolling_volatility(pd.Series([0.01, 0.02]), window=1)


def test_load_prices_missing_column_raises(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("Date,Open\n2025-01-02,100\n")

    with pytest.raises(ValueError, match="Close"):
        load_prices(bad_csv)


def test_load_prices_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_prices(tmp_path / "absent.csv")
