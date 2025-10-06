import argparse
import os
from dotenv import load_dotenv
from fetch_data import fetch_stock_data
from display_data import display_data
from store_data import store_stock_data_mysql
import yfinance as yf

load_dotenv()  # Load environment variables from .env file


def get_args_or_prompt():
    parser = argparse.ArgumentParser(
        description="Fetch, display, and store stock data.")
    parser.add_argument('--ticker', type=str,
                        help='Full ticker symbol (with suffix if any)')
    parser.add_argument('--days', type=int, help='Number of trading days')
    parser.add_argument(
        '--interval', choices=['1d', '1wk', '1mo'], help='Data interval')

    args = parser.parse_args()

    if not args.ticker:
        args.ticker = input(
            "Enter the full stock ticker symbol (with suffix if any, e.g., AAPL or RELIANCE.NS): ").strip()
    if not args.days:
        while True:
            days_str = input(
                "Enter number of trading days of historical data needed: ").strip()
            if days_str.isdigit() and int(days_str) > 0:
                args.days = int(days_str)
                break
            print("Please enter a valid positive integer for days.")
    if not args.interval:
        interval_map = {"1": "1d", "2": "1wk", "3": "1mo"}
        while True:
            print("Choose data interval:\n1: Daily\n2: Weekly\n3: Monthly")
            interval_choice = input("Enter 1, 2, or 3: ").strip()
            if interval_choice in interval_map:
                args.interval = interval_map[interval_choice]
                break
            print("Please enter 1, 2, or 3.")

    return args


def main():
    args = get_args_or_prompt()

    ticker = args.ticker.upper()
    days = args.days
    interval = args.interval

    print(
        f"Processing ticker {ticker} for last {days} days with interval {interval}.")

    stock_data = fetch_stock_data(ticker, days, interval)
    if stock_data.empty:
        print(
            f"No data returned for ticker {ticker}. Check symbol and try again.")
        return

    ticker_obj = yf.Ticker(ticker)
    exchange = ticker_obj.info.get('exchange', 'Unknown')

    display_data(stock_data, ticker, days, interval)

    # Load DB credentials from environment variables
    host = os.getenv('DB_HOST', '127.0.0.1')
    database = os.getenv('DB_NAME', 'portfolio')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'root')

    store_stock_data_mysql(stock_data, ticker, exchange,
                           host, database, user, password)


if __name__ == "__main__":
    main()
