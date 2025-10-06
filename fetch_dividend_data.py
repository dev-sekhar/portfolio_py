import yfinance as yf
import time
import pandas as pd


def fetch_dividend_data(ticker_symbol, max_retries=3, wait_seconds=5):
    print(f"Fetching dividend data for {ticker_symbol}")

    for attempt in range(max_retries):
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            dividends = ticker_obj.dividends

            # Return even if empty; caller can decide what to do
            dividends = dividends.tail(100)

            print(f"Dividend data retrieved, sample:")
            print(dividends.head())

            return dividends

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying after {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError(
                    f"Failed to fetch dividend data for {ticker_symbol} after {max_retries} attempts")
