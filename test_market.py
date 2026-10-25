"""Unit tests for the analysis logic. They don't touch the network.

Run with:  python -m unittest
"""

import unittest
from unittest.mock import patch

from market import AverageCache, calculate_avg, is_deviation, percent_change
from notifier import format_alert


class TestCalculations(unittest.TestCase):
    def test_average(self):
        self.assertEqual(calculate_avg([10, 20, 30]), 20)

    def test_average_of_empty_list_is_zero(self):
        self.assertEqual(calculate_avg([]), 0)

    def test_percent_change(self):
        self.assertAlmostEqual(percent_change(110, 100), 10.0)
        self.assertAlmostEqual(percent_change(90, 100), -10.0)

    def test_percent_change_with_zero_average(self):
        self.assertEqual(percent_change(50, 0), 0.0)

    def test_deviation_above_and_below_threshold(self):
        self.assertTrue(is_deviation(102, 100, 1.0))
        self.assertTrue(is_deviation(98, 100, 1.0))
        self.assertFalse(is_deviation(100.5, 100, 1.0))


class TestAverageCache(unittest.TestCase):
    def test_uses_cached_value_within_ttl(self):
        calls = []

        def fake_fetch(symbol):
            calls.append(symbol)
            return 100.0

        cache = AverageCache(fetch_function=fake_fetch, ttl_seconds=60)
        cache.get("AAPL")
        cache.get("AAPL")
        self.assertEqual(calls, ["AAPL"])

    def test_refetches_after_ttl_expires(self):
        calls = []

        def fake_fetch(symbol):
            calls.append(symbol)
            return 100.0

        cache = AverageCache(fetch_function=fake_fetch, ttl_seconds=60)
        with patch("market.time.time", return_value=1000):
            cache.get("AAPL")
        with patch("market.time.time", return_value=1061):
            cache.get("AAPL")
        self.assertEqual(calls, ["AAPL", "AAPL"])


class TestAlertFormat(unittest.TestCase):
    def test_rise_alert(self):
        text = format_alert("AAPL", 105.0, 100.0, 5.0)
        self.assertIn("Rise", text)
        self.assertIn("AAPL", text)
        self.assertIn("+5.00%", text)

    def test_drop_alert(self):
        self.assertIn("Drop", format_alert("AAPL", 95.0, 100.0, -5.0))


if __name__ == "__main__":
    unittest.main()
