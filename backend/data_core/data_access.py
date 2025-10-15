# --- START OF FILE backend/data_core/data_access.py ---

import pandas as pd
from typing import Any, List, Dict, Union
from .db_utils import execute_query, fetch_data_to_dataframe


def fetch_ticker_id(ticker_symbol: str) -> Union[int, None]:
    """Retrieves the internal ticker_id from the database."""
    query = "SELECT id FROM tickers WHERE symbol = %s"
    # Use execute_query to fetch a single result
    result = execute_query(query, params=(
        ticker_symbol.upper(),), fetch_one=True)
    return result['id'] if result else None


def fetch_financial_statement(ticker_id: int, statement_type: str, num_reports: int = 4) -> List[Dict[str, Any]]:
    """
    Retrieves the latest N quarterly reports for a specified financial statement 
    using a two-step process to avoid MariaDB 'LIMIT & IN/ALL/ANY/SOME subquery' error.
    """
    table_map = {
        'income_stmt': 'financials_income_stmt_quarterly',
        'balance_sheet': 'financials_balance_sheet_quarterly',
        'cash_flow': 'financials_cash_flow_quarterly'
    }

    table_name = table_map.get(statement_type)
    if not table_name:
        raise ValueError(f"Invalid statement type: {statement_type}")

    # --- Step 1: Get the N latest report dates ---
    date_query = f"""
        SELECT DISTINCT report_date
        FROM {table_name}
        WHERE ticker_id = %s
        ORDER BY report_date DESC
        LIMIT %s
    """
    # Use execute_query to fetch all dates
    date_results = execute_query(date_query, params=(
        ticker_id, num_reports), fetch_all=True)

    if not date_results:
        return []

    # Extract date strings from the result dictionaries
    report_dates = tuple(date['report_date'].strftime(
        '%Y-%m-%d') for date in date_results)
    placeholders = ', '.join(['%s'] * len(report_dates))

    # --- Step 2: Fetch all data items for those specific dates ---
    main_query = f"""
        SELECT report_date, data_item, value
        FROM {table_name}
        WHERE ticker_id = %s
        AND DATE(report_date) IN ({placeholders})
        ORDER BY report_date DESC, data_item ASC
    """
    params = (ticker_id,) + report_dates

    # Use fetch_data_to_dataframe for efficient data retrieval
    df = fetch_data_to_dataframe(main_query, params=params)

    return df.to_dict(orient="records")


def fetch_price_history(ticker_id: int, days: int) -> List[Dict[str, Any]]:
    """Retrieves the last N days of stock price and volume data."""
    query = """
        SELECT date, open, high, low, close, adj_close, volume
        FROM stock_prices
        WHERE ticker_id = %s
        ORDER BY date DESC
        LIMIT %s
    """
    # Use fetch_data_to_dataframe for efficient data retrieval
    df = fetch_data_to_dataframe(query, params=(ticker_id, days))

    # Convert date to string for JSON serialization
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    return df.to_dict(orient="records")


def fetch_latest_price(ticker_id: int) -> Union[Dict[str, Any], None]:
    """Retrieves the latest stock price and volume data."""
    query = """
        SELECT date, open, high, low, close, adj_close, volume
        FROM stock_prices
        WHERE ticker_id = %s
        ORDER BY date DESC
        LIMIT 1
    """

    # Use execute_query to fetch a single price record
    data = execute_query(query, params=(ticker_id,), fetch_one=True)

    if not data:
        return None

    # Convert date to string for JSON serialization
    data['date'] = data['date'].strftime(
        '%Y-%m-%d') if 'date' in data and hasattr(data['date'], 'strftime') else data.get('date')

    return data


def fetch_corporate_actions(ticker_id: int, action_type: str) -> List[Dict[str, Any]]:
    """Retrieves all corporate actions of a specific type for a given ticker."""
    query = """
        SELECT action_date, cash_amount, stock_ratio
        FROM corporate_actions
        WHERE ticker_id = %s AND action_type = %s
        ORDER BY action_date DESC
    """
    df = fetch_data_to_dataframe(query, params=(ticker_id, action_type))

    # Convert date to string for JSON serialization
    df['action_date'] = pd.to_datetime(df['action_date']).dt.strftime('%Y-%m-%d')

    return df.to_dict(orient="records")

def fetch_stock_news(ticker_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves the latest news articles for a given ticker."""
    query = """
        SELECT uuid, title, publisher, link, provider_publish_time, type
        FROM stock_news
        WHERE ticker_id = %s
        ORDER BY provider_publish_time DESC
        LIMIT %s
    """
    df = fetch_data_to_dataframe(query, params=(ticker_id, limit))

    # Convert datetime to string for JSON serialization
    df['provider_publish_time'] = pd.to_datetime(df['provider_publish_time']).dt.strftime('%Y-%m-%d %H:%M:%S')

    return df.to_dict(orient="records")