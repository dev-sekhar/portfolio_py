# --- START OF FILE backend/data_core/usage_access.py ---

from datetime import datetime, date
from .db_utils import execute_query
from typing import Dict, Any, Union


def get_client_usage_data(client_key: str) -> Union[Dict[str, Any], None]:
    """
    Retrieves the client's current usage and limits, and performs the daily usage reset check.
    """
    today = date.today()

    # 1. Reset/Update the daily counter (non-fetch query)
    # Resets current_daily_usage to 0 AND updates last_reset_date if the last_reset_date is NOT TODAY.
    update_query = """
        UPDATE client_usage
        SET 
            current_daily_usage = CASE WHEN last_reset_date < %s THEN 0 ELSE current_daily_usage END,
            last_reset_date = CASE WHEN last_reset_date < %s THEN %s ELSE last_reset_date END
        WHERE client_key = %s
    """
    # Execute the query via the centralized utility
    execute_query(update_query, params=(today, today, today, client_key))

    # 2. Fetch the current, updated data (fetch_one query)
    fetch_query = """
        SELECT client_name, tier, daily_limit, monthly_limit, current_daily_usage
        FROM client_usage
        WHERE client_key = %s
    """
    # Fetch the result via the centralized utility
    return execute_query(fetch_query, params=(client_key,), fetch_one=True)


def increment_client_usage(client_key: str, amount: int = 1) -> bool:
    """
    Increments the client's usage counters, checking the limit before committing.
    """

    # 1. First, call the check function to ensure daily reset happened
    # This also acts as a data retrieval for the check below
    current_data = get_client_usage_data(client_key)

    if not current_data:
        return False

    # 2. Check if daily usage is over the limit BEFORE incrementing
    if current_data['current_daily_usage'] + amount > current_data['daily_limit']:
        return False

    # 3. Increment usage (non-fetch query)
    increment_query = """
        UPDATE client_usage
        SET current_daily_usage = current_daily_usage + %s,
            current_monthly_usage = current_monthly_usage + %s
        WHERE client_key = %s
    """
    # Execute the increment via the centralized utility
    execute_query(increment_query, params=(amount, amount, client_key))

    # We can assume success if the increment was not aborted by the limit check and no exception was raised
    return True

# --- END OF FILE backend/data_core/usage_access.py ---
