from .db_connection import get_db_connection, get_db_engine
from mysql.connector import Error
import pandas as pd
from typing import Any, List, Tuple

def execute_query(sql_query: str, params: Tuple[Any, ...] = None, fetch_one: bool = False, fetch_all: bool = False) -> Any:
    """
    Executes a SQL query and handles the database connection lifecycle.

    :param sql_query: The SQL query string.
    :param params: A tuple of parameters for the query.
    :param fetch_one: If True, returns the result of cursor.fetchone().
    :param fetch_all: If True, returns the result of cursor.fetchall().
    :return: The result of the fetch operation, or None for non-select queries.
    """
    conn = None
    result = None
    
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ DB Connection failed in db_utils.")
            return None
        
        # Use a dictionary cursor for SELECT queries for named columns
        cursor = conn.cursor(dictionary=fetch_one or fetch_all)
        
        cursor.execute(sql_query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        # Commit changes for non-SELECT queries (INSERT, UPDATE, DELETE)
        if not (fetch_one or fetch_all):
            conn.commit()
            
    except Error as e:
        print(f"❌ MySQL Error during query execution: {e}\nQuery: {sql_query}")
        result = None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
    return result

def fetch_data_to_dataframe(sql_query: str, params: Tuple[Any, ...] = None) -> pd.DataFrame:
    """
    Executes a SQL query and returns the results as a Pandas DataFrame using SQLAlchemy.
    
    :param sql_query: The SQL query string.
    :param params: A tuple of parameters for the query.
    :return: A Pandas DataFrame.
    """
    try:
        engine = get_db_engine()
        df = pd.read_sql(sql_query, engine, params=params)
        return df
    except Exception as e:
        print(f"❌ Error during DataFrame fetch: {e}\nQuery: {sql_query}")
        return pd.DataFrame()