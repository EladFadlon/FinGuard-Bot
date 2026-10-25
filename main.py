"""FinGuard-Bot: command-line watchlist with Telegram alerts on price deviations."""

import logging
import time
from datetime import datetime

from dotenv import load_dotenv

from market import AverageCache, get_current_price, is_deviation, is_valid_ticker, percent_change
from notifier import format_alert, send_telegram_message

CHECK_INTERVAL_SECONDS = 180
DEVIATION_THRESHOLD_PCT = 1.0

MENU = """
~~~~~~~~~~ Fin-Bot Menu ~~~~~~~~~~
    1. Show current watchlist
    2. Add stock to watchlist
    3. Remove stock from watchlist
    4. Start monitoring (live)
    5. Exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Select an option: """


def show_watchlist(watchlist):
    if not watchlist:
        print("Watchlist is currently empty.")
    else:
        print(f"\nCurrently watching: {', '.join(watchlist)}")


def add_stock(watchlist):
    symbol = input("Enter stock ticker: ").strip().upper()
    while symbol != "Q":
        if symbol in watchlist:
            print(f"{symbol} is already in the watchlist.")
            return
        if is_valid_ticker(symbol):
            watchlist.append(symbol)
            print(f"{symbol} added successfully!")
            logging.info(f"User added stock: {symbol}")
            return
        symbol = input(f"{symbol} not found. Enter a different ticker (or 'Q' to cancel): ").strip().upper()
    print("Action cancelled, returning to menu.")


def remove_stock(watchlist):
    if not watchlist:
        print("Watchlist is empty, nothing to remove.")
        return
    symbol = input("Enter stock ticker to remove: ").strip().upper()
    if symbol in watchlist:
        watchlist.remove(symbol)
        print(f"{symbol} was removed successfully!")
        logging.info(f"User removed stock: {symbol}")
    else:
        print(f"{symbol} is not in your watchlist.")


def check_stock(symbol, averages):
    """Check one stock and send an alert if it deviates. Errors are logged, not raised."""
    try:
        average = averages.get(symbol)
        current_price = get_current_price(symbol)
    except Exception as e:
        # Network failure, API change or delisted symbol: skip this stock for now.
        logging.error(f"Failed to fetch data for {symbol}: {e}")
        print(f"Could not fetch data for {symbol}, will retry next cycle.")
        return

    if not average:
        logging.warning(f"No price history for {symbol}, skipping.")
        return

    change = percent_change(current_price, average)
    print(f"Checking {symbol}... | Price: {current_price:.2f} | Avg: {average:.2f} | Change: {change:+.2f}%")

    if is_deviation(current_price, average, DEVIATION_THRESHOLD_PCT):
        logging.warning(f"DEVIATION DETECTED: {symbol} at {current_price:.2f} ({change:+.2f}%)")
        send_telegram_message(format_alert(symbol, current_price, average, change))


def monitor(watchlist):
    if not watchlist:
        print("Watchlist is empty. Add a stock first.")
        return

    averages = AverageCache()
    print("Monitoring started. Press Ctrl+C to stop.")
    try:
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{now}] Checking {len(watchlist)} stocks...")
            for symbol in watchlist:
                check_stock(symbol, averages)
            print(f"--- Check completed. Next check in {CHECK_INTERVAL_SECONDS} seconds ---")
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nMonitoring stopped. Returning to menu.")


def main():
    load_dotenv()
    logging.basicConfig(
        filename="fin_bot.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    watchlist = []
    actions = {
        "1": show_watchlist,
        "2": add_stock,
        "3": remove_stock,
        "4": monitor,
    }

    while True:
        choice = input(MENU).strip()
        if choice == "5":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option, please enter a number between 1 and 5.")
        else:
            action(watchlist)


if __name__ == "__main__":
    main()
