import os

import requests
import yfinance
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Token found: {os.getenv('TELEGRAM_TOKEN') is not None}")

logging.basicConfig(
    filename='fin_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )


def send_telegram_message(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not token or not chat_id:
        print("Error: Telegram credentials not found in .env file!")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}&parse_mode=Markdown"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Telegram Notification Sent!")
        else:
            print(f"Failed to send telegram: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")


def is_valid_ticker(symbol):
    try:
        tick = yfinance.Ticker(symbol)
        hist = tick.history(period="1d")
        if hist.empty:
            logging.warning(f"Ticker {symbol} returned empty history (might not exist).")
            return False
        return True
    except Exception as e:
        logging.error(f"API Error while validating {symbol}: {e}")
        return False


def calculate_avg(price_list):
    if len(price_list) == 0:
        return 0
    return sum(price_list) / len(price_list)


def show_menu():
    menu_text = """~~~~~~~~~~ Fin-Bot Menu ~~~~~~~~~~
    -1.Show Current WatchList.
    -2.Add New Stock To WatchList.
    -3.Remove Stock From WatchList.
    -4.Start Monitoring (Live).
    -5.Exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Select An Option: """
    return input(menu_text)


if __name__ == "__main__":
    watched_stocks = []

    while True:
        choice = show_menu()
        if choice == "1":
            if len(watched_stocks) == 0:
                print("WatchList is currently Empty.. ")
            else:
                print(f"\nCurrently Watching: {watched_stocks}")
        elif choice == "2":
            new_stock = input("Enter Stock Ticker: ").upper()
            if new_stock in watched_stocks:
                print(f"{new_stock} Is Already in WatchList")
            else:
                while new_stock != 'Q' and not is_valid_ticker(new_stock):
                    new_stock = input(f"{new_stock} Not Found.. Enter New Ticker (Or 'Q' to Cancel): ").upper()
                if new_stock != 'Q':
                    watched_stocks.append(new_stock)
                    print(f"{new_stock} Added Successfully! ")
                    logging.info(f"User added stock: {new_stock}")
                else:
                    print("Action Cancelled, Returning to Menu..")
        elif choice == "3":
            to_remove = input("Enter Stock Ticker: ").upper()
            while not to_remove in watched_stocks:
                print(f"{to_remove} Is Not In Your WatchList..")
                to_remove = input("Enter Stock Ticker: ")
            else:
                watched_stocks.remove(to_remove)
                print(f"{to_remove} Was Removed Successfully! ")
        elif choice == "4":
            averages_cache = {}
            try:
                while True:
                    from datetime import datetime
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{now}] Info: Starting check for {len(watched_stocks)} stocks...")
                    for stock in watched_stocks:
                        if stock not in averages_cache:
                            print(f"Calculating initial average for {stock}...")
                            ticker = yfinance.Ticker(stock)
                            history = ticker.history(period="5d")
                            averages_cache[stock] = calculate_avg(history['Close'].tolist())

                        ticker = yfinance.Ticker(stock)
                        current_price = ticker.fast_info['last_price']
                        avg = averages_cache[stock]

                        print(f"Checking {stock}... | Price: {current_price:.4f} | Avg: {avg:.4f}")
                        diff = ((current_price / avg) - 1) * 100
                        icon = "📈" if diff > 0 else "📉"
                        status = "Movement" if diff > 0 else "Drop"
                        if current_price > avg * 1.01 or current_price < avg * 0.99 :
                            logging.warning(f"DEVIATION DETECTED: {stock} at {current_price}")
                            alert_msg = f"""
🚀 *Stock {status} Alert* {icon}
---
*Stock:* {stock}
*Current Price:* `${current_price:.2f}`
*5-Day Average:* `${avg:.2f}`
*Change:* `{diff:.2f}%`
---
_Check your portfolio!_
"""
                            print(alert_msg)
                            send_telegram_message(alert_msg)
                    print(f"\n--- Check completed. Next check in 180 seconds... ---")
                    time.sleep(180)
            except KeyboardInterrupt:
                print("\nMonitoring Stopped. Returning to Menu....")
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid Option, Please Enter a Number Between 1-5")
