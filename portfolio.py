import argparse
from dotenv import load_dotenv
import yfinance as yf
from fetch_price_data import fetch_stock_data
from fetch_dividend_data import fetch_dividend_data
from display_data import display_data, display_dividends
from store_data import store_stock_data_mysql, store_corporate_actions_mysql

load_dotenv()  # Load environment variables from .env file


def get_args_or_prompt():
    parser = argparse.ArgumentParser(
        description="Fetch, display, and store stock data.")
    parser.add_argument('--ticker', type=str,
                        help='Full stock ticker symbol (with suffix if any)')
    parser.add_argument('--days', type=int, help='Number of trading days')
    parser.add_argument(
        '--interval', choices=['1d', '1wk', '1mo'], help='Data interval')
    parser.add_argument(
        '--data-type', choices=['price', 'dividend', 'both'], help="Choose data type: 'price', 'dividend', or 'both'")

    args = parser.parse_args()

    if not args.ticker:
        args.ticker = input(
            "Enter the full stock ticker symbol (with suffix if any, e.g., AAPL or RELIANCE.NS): ").strip()

    if not args.data_type:
        data_type_map = {"1": "price", "2": "dividend", "3": "both"}
        while True:
            print("Choose data type to fetch:")
            print("1: Price")
            print("2: Dividend")
            print("3: Both Price and Dividend")
            choice = input("Enter 1, 2, or 3: ").strip()
            if choice in data_type_map:
                args.data_type = data_type_map[choice]
                break
            else:
                print("Please enter 1, 2, or 3.")

    if args.data_type in ('price', 'both'):
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
                print("Choose data interval:")
                print("1: Daily")
                print("2: Weekly")
                print("3: Monthly")
                interval_choice = input("Enter 1, 2, or 3: ").strip()
                if interval_choice in interval_map:
                    args.interval = interval_map[interval_choice]
                    break
                print("Please enter 1, 2, or 3.")

    return args


def main():
    print("Starting portfolio.py")
    args = get_args_or_prompt()

    ticker = args.ticker.upper()
    data_type = args.data_type

    ticker_obj = yf.Ticker(ticker)
    exchange = ticker_obj.info.get('exchange', 'Unknown')

    # Fetch price data if requested
    if data_type in ('price', 'both'):
        days = args.days
        interval = args.interval
        print(
            f"Processing ticker {ticker} for last {days} days with interval {interval} (Price data).")

        stock_data = fetch_stock_data(ticker, days, interval)
        if stock_data.empty:
            print(
                f"No price data returned for ticker {ticker}. Check symbol and try again.")
        else:
            display_data(stock_data, ticker, days, interval)
            store_stock_data_mysql(stock_data, ticker, exchange)

    # Fetch dividend data if requested
    if data_type in ('dividend', 'both'):
        print(f"Processing ticker {ticker} for dividend history.")

        dividends = fetch_dividend_data(ticker)
        if dividends.empty:
            print(f"No dividend data found for ticker {ticker}.")
        else:
            display_dividends(dividends, ticker)
            store_corporate_actions_mysql(
                dividends, ticker, exchange, action_type='dividend')


if __name__ == "__main__":
    main()
