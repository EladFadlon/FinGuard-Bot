"""Sending alerts to Telegram."""

import logging
import os

import requests

REQUEST_TIMEOUT_SECONDS = 10


def format_alert(symbol, current_price, average, change_pct):
    """Build the Telegram alert text for a price deviation."""
    icon = "📈" if change_pct > 0 else "📉"
    status = "Rise" if change_pct > 0 else "Drop"
    return (
        f"🚨 *Stock {status} Alert* {icon}\n"
        f"---\n"
        f"*Stock:* {symbol}\n"
        f"*Current Price:* `${current_price:.2f}`\n"
        f"*5-Day Average:* `${average:.2f}`\n"
        f"*Change:* `{change_pct:+.2f}%`\n"
        f"---\n"
        f"_Check your portfolio!_"
    )


def send_telegram_message(message):
    """Send a message through the Telegram Bot API. Returns True on success."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not token or not chat_id:
        logging.error("Telegram credentials missing (TELEGRAM_TOKEN / CHAT_ID).")
        print("Error: Telegram credentials not found in .env file!")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # Passing the text as params lets requests URL-encode it (newlines, $, %, etc.).
    params = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as e:
        logging.error(f"Network error sending to Telegram: {e}")
        print(f"Error sending to Telegram: {e}")
        return False

    if response.status_code != 200:
        logging.error(f"Telegram returned {response.status_code}: {response.text}")
        print(f"Failed to send Telegram message: {response.status_code}")
        return False

    print("Telegram notification sent!")
    return True
