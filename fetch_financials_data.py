# --- START OF FILE fetch_financials_data.py ---

import yfinance as yf
import pandas as pd
import time


def fetch_quarterly_financials(ticker_symbol, max_retries=3, wait_seconds=5):
    """
    Fetches the quarterly Income Statement, Balance Sheet, and Cash Flow 
    for a given ticker symbol.

    Returns a dictionary of Pandas DataFrames.
    """
    print(f"Fetching quarterly financials for {ticker_symbol}")

    for attempt in range(max_retries):
        try:
            ticker_obj = yf.Ticker(ticker_symbol)

            # Ticker.quarterly_income_stmt is the dedicated method for quarterly IS
            q_income = ticker_obj.quarterly_income_stmt
            q_balance_sheet = ticker_obj.quarterly_balance_sheet
            q_cash_flow = ticker_obj.quarterly_cash_flow

            if q_income.empty and q_balance_sheet.empty and q_cash_flow.empty:
                raise ValueError("No fundamental data found for this ticker.")

            print("Quarterly financial data retrieved.")

            return {
                'income_statement': q_income,
                'balance_sheet': q_balance_sheet,
                'cash_flow': q_cash_flow
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying after {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                raise RuntimeError(
                    f"Failed to fetch quarterly financials for {ticker_symbol} after {max_retries} attempts")

# --- END OF FILE fetch_financials_data.py ---
