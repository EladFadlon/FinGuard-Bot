# FinGuard-Bot 📈 🚨

FinGuard-Bot is a professional-grade monitoring tool designed to track stock market volatility in real-time. Built by a Computer Science student at Ben-Gurion University, the project integrates live financial data with automated mobile notifications. It emphasizes software engineering best practices, including defensive programming, efficient data caching (Memoization), and secure credential management

## 🚀 Features
- **Live Monitoring:** Fetches real-time price data using `yfinance`.
- **Smart Analysis:** Compares current prices against a 5-day moving average to detect volatility.
- **Instant Alerts:** Integrated with Telegram Bot API for real-time mobile notifications.
- **Optimization:** Implemented a **Memoization** mechanism to reduce redundant API calls for historical data.
- **Defensive Programming:** Robust error handling for network issues and invalid ticker symbols.
- **Logging:** Full traceability with a persistent logging system (`fin_bot.log`).

## 🛠️ Tech Stack
- **Language:** Python
- **APIs:** Yahoo Finance (yfinance), Telegram Bot API
- **Libraries:** Requests, Logging, Datetime

## 🏗️ Architecture Highlights
- **Modular Design:** Separation of concerns between data fetching, analysis, and notification.
- **Efficiency:** Uses a caching system (Dictionary-based) to store calculated averages.
- **User Interface:** Interactive Command Line Interface (CLI) for managing the watchlist.

## 📋 How to Use
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file with your `TELEGRAM_TOKEN` and `CHAT_ID`.
4. Run `python main.py`.
