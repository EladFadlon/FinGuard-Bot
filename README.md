# FinGuard-Bot 📈🚨

A command-line stock watchlist that checks prices every few minutes and sends a **Telegram alert** when a stock moves more than 1% away from its 5-day average.

## Features

- **Watchlist management:** add and remove stocks from an interactive CLI menu. Tickers are validated against Yahoo Finance before they are added.
- **Live monitoring:** checks the current price of every stock in the watchlist every 3 minutes.
- **Deviation detection:** compares each price to its 5-day average closing price and flags moves larger than ±1%.
- **Telegram alerts:** sends a formatted message to your phone through the Telegram Bot API.
- **Caching with expiry:** 5-day averages are cached so they aren't re-downloaded on every check, and refreshed every 6 hours so they don't go stale.
- **Error handling:** a network failure or a bad symbol is logged and skipped, and the bot keeps running and retries on the next cycle.
- **Logging:** user actions, alerts and errors are written to `fin_bot.log`.

## Example alert

```
🚨 Stock Rise Alert 📈
---
Stock: AAPL
Current Price: $105.00
5-Day Average: $100.00
Change: +5.00%
---
Check your portfolio!
```

## Project Structure

| File | Responsibility |
|---|---|
| `main.py` | CLI menu and the monitoring loop |
| `market.py` | Price data from Yahoo Finance, deviation math, `AverageCache` |
| `notifier.py` | Formatting and sending Telegram alerts |
| `test_market.py` | Unit tests for the calculation, caching and formatting logic |

## Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/EladFadlon/FinGuard-Bot.git
   cd FinGuard-Bot
   pip install -r requirements.txt
   ```
2. Create a Telegram bot with [@BotFather](https://t.me/BotFather) and get its token. Then get your chat ID, for example by messaging [@userinfobot](https://t.me/userinfobot).
3. Create a `.env` file in the project folder:
   ```
   TELEGRAM_TOKEN=your-bot-token
   CHAT_ID=your-chat-id
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Running the tests

```bash
python -m unittest -v
```

The tests use no network: the cache is tested with a fake fetch function and a mocked clock.

## Configuration

The settings are constants at the top of the files:

| Setting | Default | Where |
|---|---|---|
| `CHECK_INTERVAL_SECONDS` | 180 | `main.py` |
| `DEVIATION_THRESHOLD_PCT` | 1.0 | `main.py` |
| `AVERAGE_PERIOD` | `"5d"` | `market.py` |
| `CACHE_TTL_SECONDS` | 6 hours | `market.py` |

## Tech Stack

Python, [yfinance](https://github.com/ranaroussi/yfinance), Telegram Bot API, `requests`, `python-dotenv`, `unittest`.
