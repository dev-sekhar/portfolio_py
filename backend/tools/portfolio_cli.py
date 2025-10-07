import argparse
from dotenv import load_dotenv
import yfinance as yf
# Corrected Imports for the new structure:
from ..data_core.fetch.fetch_price_data import fetch_stock_data
from ..data_core.fetch.fetch_dividend_data import fetch_dividend_data
from ..data_core.fetch.fetch_splits_data import fetch_split_data
from ..data_core.fetch.fetch_financials_data import fetch_quarterly_financials
from .display_data import display_data, display_dividends, display_splits, display_financials
from ..data_core.store.store_data import store_stock_data_mysql, store_corporate_actions_mysql, store_financials_mysql


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
        '--data-type', choices=['price', 'dividend', 'split', 'financials', 'all'], help="Choose data type: 'price', 'dividend', 'split', 'financials', or 'all'")

    args = parser.parse_args()

    if not args.ticker:
        args.ticker = input(
            "Enter the full stock ticker symbol (with suffix if any, e.g., AAPL or RELIANCE.NS): ").strip()

    if not args.data_type:
        data_type_map = {"1": "price",
                         "2": "dividend", "3": "split", "4": "financials", "5": "all"}
        while True:
            print("Choose data type to fetch:")
            print("1: Price")
            print("2: Dividend")
            print("3: Split")
            print("4: Quarterly Financials (Income, Balance Sheet, Cash Flow)")
            print("5: All")
            choice = input("Enter 1, 2, 3, 4, or 5: ").strip()
            if choice in data_type_map:
                args.data_type = data_type_map[choice]
                break
            else:
                print("Please enter 1, 2, 3, 4, or 5.")

    if args.data_type in ('price', 'all'):
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
    print("Starting portfolio_cli.py")
    args = get_args_or_prompt()

    ticker = args.ticker.upper()
    data_type = args.data_type

    # Use a try/except for ticker_obj.info access in case of bad ticker
    try:
        ticker_obj = yf.Ticker(ticker)
        exchange = ticker_obj.info.get('exchange', 'Unknown')
    except Exception:
        print(
            f"Error: Could not retrieve info for ticker {ticker}. Check symbol and try again.")
        return

    # Fetch price data if requested or if 'all' selected
    if data_type in ('price', 'all'):
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

    # Fetch dividend data if requested or if 'all' selected
    if data_type in ('dividend', 'all'):
        print(f"Processing ticker {ticker} for dividend history.")

        dividends = fetch_dividend_data(ticker)
        if dividends.empty:
            print(f"No dividend data found for ticker {ticker}.")
        else:
            display_dividends(dividends, ticker)
            store_corporate_actions_mysql(
                dividends, ticker, exchange, action_type='dividend')

    # Fetch split data if requested or if 'all' selected
    if data_type in ('split', 'all'):
        print(f"Processing ticker {ticker} for split history.")

        splits = fetch_split_data(ticker)
        if splits.empty:
            print(f"No split data found for ticker {ticker}.")
        else:
            display_splits(splits, ticker)
            store_corporate_actions_mysql(
                splits, ticker, exchange, action_type='split')

    # Fetch financials data if requested or if 'all' selected
    if data_type in ('financials', 'all'):
        print(f"Processing ticker {ticker} for quarterly financials.")

        financials_data = fetch_quarterly_financials(ticker)

        # Check if any statement has data
        if not any(not df.empty for df in financials_data.values()):
            print(f"No quarterly financials found for ticker {ticker}.")
        else:
            display_financials(financials_data, ticker)
            store_financials_mysql(financials_data, ticker)


if __name__ == "__main__":
    main()
