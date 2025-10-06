import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import time


def fetch_stock_data(ticker_symbol, num_days, interval, max_retries=3, wait_seconds=5):
    end_date = datetime.today() - timedelta(days=1)
    extended_start_date = end_date - timedelta(days=num_days * 3)
    end_date_str = end_date.strftime('%Y-%m-%d')
    extended_start_date_str = extended_start_date.strftime('%Y-%m-%d')

    print(
        f"Fetching data for {ticker_symbol} from {extended_start_date_str} to {end_date_str} with interval {interval}")

    for attempt in range(max_retries):
        try:
            stock_data = yf.download(
                ticker_symbol,
                start=extended_start_date_str,
                end=end_date_str,
                interval=interval,
                auto_adjust=True,
                progress=False,
            )
            if stock_data.empty:
                raise ValueError("No data found for ticker or date range.")

            # Flatten MultiIndex columns if present
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.get_level_values(0)

            # Convert PeriodIndex to DatetimeIndex if needed
            if isinstance(stock_data.index, pd.PeriodIndex):
                stock_data.index = stock_data.index.to_timestamp(how='start')

            print("Data columns:", stock_data.columns)
            print(stock_data.head())

            return stock_data.tail(num_days)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying after {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError(
                    f"Failed to fetch data for {ticker_symbol} after {max_retries} attempts")
