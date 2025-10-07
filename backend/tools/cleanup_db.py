import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from ..data_core.db_connection import get_db_connection  # Import the function

# Load environment variables just like in portfolio.py
load_dotenv()


def cleanup_database():
    connection = None
    try:
        # Use the standard connection function, relying on it to load credentials from .env
        connection = get_db_connection()

        if connection and connection.is_connected():
            print("Connected to MySQL database via db_connection.py")
        else:
            print("❌ Unable to connect to database for cleanup.")
            return

        cursor = connection.cursor()

        # Disable foreign key checks to allow truncating tables with foreign keys
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # List of ALL data tables to truncate (excluding the core 'tickers' which is last)
        tables_to_truncate = [
            "stock_prices",
            "corporate_actions",  # <-- INCLUDED CORPORATE ACTIONS
            "financials_income_stmt_quarterly",
            "financials_balance_sheet_quarterly",
            "financials_cash_flow_quarterly",
        ]

        for table in tables_to_truncate:
            try:
                # TRUNCATE TABLE is much faster than DELETE FROM
                cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"TRUNCATED table: {table}")
            except Error as e:
                # Handle cases where a table might not exist yet
                if 'Unknown table' in str(e):
                    print(
                        f"Warning: Table {table} does not exist yet. Skipping.")
                else:
                    print(f"Error truncating table {table}: {e}")

        # Tickers table is truncated last as other tables are dependent on it
        try:
            cursor.execute("TRUNCATE TABLE tickers")
            print("TRUNCATED table: tickers")
        except Error as e:
            if 'Unknown table' in str(e):
                print(f"Warning: Table tickers does not exist yet. Skipping.")
            else:
                print(f"Error truncating table tickers: {e}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        connection.commit()
        print("✅ Database cleanup completed: All data tables have been cleared.")

    except Error as e:
        print(f"❌ MySQL Error during database cleanup: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed.")


if __name__ == "__main__":
    # No need to pass credentials, get_db_connection handles it via .env
    cleanup_database()
