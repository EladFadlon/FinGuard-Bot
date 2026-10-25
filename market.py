"""Market data: fetching prices from Yahoo Finance and detecting deviations."""

import logging
import time

import yfinance

AVERAGE_PERIOD = "5d"           # history window used for the moving average
CACHE_TTL_SECONDS = 6 * 60 * 60  # recompute a cached average after 6 hours


def calculate_avg(price_list):
    """Return the arithmetic mean of a list of prices (0 for an empty list)."""
    if len(price_list) == 0:
        return 0
    return sum(price_list) / len(price_list)


def percent_change(current_price, average):
    """Percentage difference of current_price relative to average."""
    if average == 0:
        return 0.0
    return (current_price / average - 1) * 100


def is_deviation(current_price, average, threshold_pct):
    """True if the price moved more than threshold_pct percent away from the average."""
    return abs(percent_change(current_price, average)) > threshold_pct


def is_valid_ticker(symbol):
    """Check that Yahoo Finance returns price history for this symbol."""
    try:
        history = yfinance.Ticker(symbol).history(period="1d")
    except Exception as e:
        logging.error(f"API error while validating {symbol}: {e}")
        return False
    if history.empty:
        logging.warning(f"Ticker {symbol} returned empty history (might not exist).")
        return False
    return True


def get_current_price(symbol):
    """Latest traded price for symbol."""
    return yfinance.Ticker(symbol).fast_info["last_price"]


def fetch_average(symbol):
    """Average closing price over AVERAGE_PERIOD."""
    history = yfinance.Ticker(symbol).history(period=AVERAGE_PERIOD)
    return calculate_avg(history["Close"].tolist())


class AverageCache:
    """Caches each symbol's moving average so it isn't re-fetched on every check.

    Entries expire after ttl_seconds, so a bot that runs for days keeps
    comparing against a fresh average instead of a stale one.
    """

    def __init__(self, fetch_function=fetch_average, ttl_seconds=CACHE_TTL_SECONDS):
        self._fetch = fetch_function
        self._ttl = ttl_seconds
        self._entries = {}  # symbol -> (average, time it was computed)

    def get(self, symbol):
        entry = self._entries.get(symbol)
        if entry is not None:
            average, computed_at = entry
            if time.time() - computed_at < self._ttl:
                return average

        average = self._fetch(symbol)
        self._entries[symbol] = (average, time.time())
        return average
