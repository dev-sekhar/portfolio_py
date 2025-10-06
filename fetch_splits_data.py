import yfinance as yf
import time
import pandas as pd


def fetch_split_data(ticker_symbol, max_retries=3, wait_seconds=5):
    print(f"Fetching split data for {ticker_symbol}")
    for attempt in range(max_retries):
        try:
            ticker_obj = yf.Ticker(ticker_symbol)
            splits = ticker_obj.splits.tail(100)  # last 100 splits
            print("Split data retrieved, sample:")
            print(splits.head())
            return splits
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(wait_seconds)
            else:
                raise RuntimeError(
                    f"Failed to fetch split data for {ticker_symbol}")
