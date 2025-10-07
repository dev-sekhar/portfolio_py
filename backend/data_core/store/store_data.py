import pandas as pd
from mysql.connector import Error
from ..db_connection import get_db_connection


def index_exists(cursor, table_name, index_name):
    cursor.execute("""
        SELECT COUNT(1)
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE table_schema = DATABASE() AND table_name = %s AND index_name = %s
    """, (table_name, index_name))
    return cursor.fetchone()[0] > 0


def foreign_key_exists(cursor, table_name, fk_name):
    cursor.execute("""
        SELECT COUNT(1)
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
        WHERE table_schema = DATABASE() AND table_name = %s 
        AND constraint_name = %s AND constraint_type = 'FOREIGN KEY'
    """, (table_name, fk_name))
    return cursor.fetchone()[0] > 0


def store_stock_data_mysql(stock_data, ticker_symbol, exchange):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Unable to connect to database for stock price storage.")
            return

        cursor = connection.cursor()

        # Ensure tickers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(16) UNIQUE NOT NULL,
                exchange VARCHAR(16)
            )
        """)
        connection.commit()

        # Insert or update ticker record
        cursor.execute("SELECT id FROM tickers WHERE symbol=%s",
                       (ticker_symbol,))
        row = cursor.fetchone()
        if row:
            ticker_id = row[0]
            cursor.execute(
                "UPDATE tickers SET exchange=%s WHERE id=%s", (exchange, ticker_id))
        else:
            cursor.execute(
                "INSERT INTO tickers (symbol, exchange) VALUES (%s, %s)", (ticker_symbol, exchange))
            ticker_id = cursor.lastrowid
        connection.commit()

        # Ensure stock_prices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                ticker_id INT NOT NULL,
                date DATE NOT NULL,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                adj_close FLOAT,
                volume BIGINT,
                exchange VARCHAR(16),
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (ticker_id, date),
                FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
            )
        """)
        connection.commit()

        adj_close_col = 'Adj Close' if 'Adj Close' in stock_data.columns else 'Close'

        insert_query = """
            INSERT INTO stock_prices (ticker_id, date, open, high, low, close, adj_close, volume, exchange)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                open=VALUES(open), high=VALUES(high), low=VALUES(low), close=VALUES(close), 
                adj_close=VALUES(adj_close), volume=VALUES(volume), 
                last_modified=CURRENT_TIMESTAMP, exchange=VALUES(exchange)
        """

        print(f"📊 Inserting/updating {len(stock_data)} stock price records...")
        for idx, row in stock_data.iterrows():
            record_date = idx.date() if hasattr(idx, 'date') else idx
            data_tuple = (
                ticker_id,
                record_date,
                float(row['Open']) if pd.notna(row['Open']) else None,
                float(row['High']) if pd.notna(row['High']) else None,
                float(row['Low']) if pd.notna(row['Low']) else None,
                float(row['Close']) if pd.notna(row['Close']) else None,
                float(row[adj_close_col]) if pd.notna(
                    row[adj_close_col]) else None,
                int(row['Volume']) if pd.notna(row['Volume']) else 0,
                exchange,
            )
            try:
                cursor.execute(insert_query, data_tuple)
                print(f"✔️ Inserted/updated price record for {record_date}")
            except Error as e:
                print(
                    f"❌ MySQL Error inserting stock price {record_date}: {e}")
        connection.commit()
        print("✅ Stock price data committed successfully.")

    except Error as e:
        print(f"❌ MySQL Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed for stock prices.")


def store_corporate_actions_mysql(corp_action_data, ticker_symbol, exchange, action_type='dividend'):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Unable to connect to database for corporate action storage.")
            return

        cursor = connection.cursor()

        # Ensure tickers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(16) UNIQUE NOT NULL,
                exchange VARCHAR(16)
            )
        """)
        connection.commit()

        # Insert or update ticker record
        cursor.execute("SELECT id FROM tickers WHERE symbol=%s",
                       (ticker_symbol,))
        row = cursor.fetchone()
        if row:
            ticker_id = row[0]
            cursor.execute(
                "UPDATE tickers SET exchange=%s WHERE id=%s", (exchange, ticker_id))
        else:
            cursor.execute(
                "INSERT INTO tickers (symbol, exchange) VALUES (%s, %s)", (ticker_symbol, exchange))
            ticker_id = cursor.lastrowid
        connection.commit()

        # Ensure corporate_actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corporate_actions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticker_id INT NOT NULL,
                action_type VARCHAR(32) NOT NULL,
                action_date DATE NOT NULL,
                cash_amount FLOAT DEFAULT NULL,
                stock_ratio FLOAT DEFAULT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE,
                UNIQUE KEY uniq_action (ticker_id, action_type, action_date)
            )
        """)
        connection.commit()

        insert_query = """
            INSERT INTO corporate_actions (
                ticker_id, action_type, action_date, cash_amount, stock_ratio, description
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cash_amount=VALUES(cash_amount),
                stock_ratio=VALUES(stock_ratio),
                description=VALUES(description),
                created_at=CURRENT_TIMESTAMP
        """

        print(
            f"📊 Inserting/updating {len(corp_action_data)} corporate action records...")
        for action_date, amount in corp_action_data.items():
            if action_type == 'dividend':
                data_tuple = (
                    ticker_id,
                    action_type,
                    action_date,
                    float(amount) if pd.notna(amount) else None,
                    None,
                    None
                )
            elif action_type == 'split':
                data_tuple = (
                    ticker_id,
                    action_type,
                    action_date,
                    None,
                    float(amount) if pd.notna(amount) else None,
                    None
                )
            else:
                data_tuple = (
                    ticker_id,
                    action_type,
                    action_date,
                    None,
                    None,
                    None
                )

            try:
                cursor.execute(insert_query, data_tuple)
                print(f"✔️ Inserted/updated {action_type} for {action_date}")
            except Error as e:
                print(
                    f"❌ MySQL Error inserting {action_type} on {action_date}: {e}")
        connection.commit()
        print("✅ Corporate actions committed successfully.")

    except Error as e:
        print(f"❌ MySQL Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed for corporate actions.")


# --- UPDATE store_data.py ---
# ... (all existing imports and functions: index_exists, foreign_key_exists,
#       store_stock_data_mysql, store_corporate_actions_mysql)

def store_financials_mysql(financials_data: dict, ticker_symbol: str):
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            print("❌ Unable to connect to database for financials storage.")
            return

        cursor = connection.cursor()

        # 1. Ensure tickers table and get ticker_id (copied from existing functions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(16) UNIQUE NOT NULL,
                exchange VARCHAR(16)
            )
        """)
        connection.commit()
        cursor.execute("SELECT id FROM tickers WHERE symbol=%s",
                       (ticker_symbol,))
        row = cursor.fetchone()
        if not row:
            # Need to create the ticker entry if it doesn't exist.
            # Assuming exchange is not needed for this check, but would be good practice
            # to pass it through from portfolio.py if possible.
            print(
                f"⚠️ Ticker {ticker_symbol} not found in database. Please run price fetch first or update 'exchange' logic.")
            return
        ticker_id = row[0]
        connection.commit()

        # 2. Define table structures for financials
        # Dynamic creation/update of columns is complex. We will use a flexible structure
        # where we ensure the table and then insert all rows/columns.

        # Function to ensure a table exists with the required columns
        def ensure_financials_table(table_name):
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    ticker_id INT NOT NULL,
                    report_date DATE NOT NULL,
                    data_item VARCHAR(128) NOT NULL,
                    value BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (ticker_id, report_date, data_item),
                    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
                )
            """)
            connection.commit()
            print(f"Ensured table {table_name} exists.")

        # Table names mapping
        table_map = {
            'income_statement': 'financials_income_stmt_quarterly',
            'balance_sheet': 'financials_balance_sheet_quarterly',
            'cash_flow': 'financials_cash_flow_quarterly'
        }

        # 3. Process and store each statement
        for statement_name, df in financials_data.items():
            if df is None or df.empty:
                print(f"Skipping empty data for {statement_name}")
                continue

            table_name = table_map[statement_name]
            ensure_financials_table(table_name)

            insert_query = f"""
                INSERT INTO {table_name} (ticker_id, report_date, data_item, value)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    value=VALUES(value), created_at=CURRENT_TIMESTAMP
            """

            print(f"📊 Inserting/updating {statement_name} records...")

            # DataFrame is indexed by data item (row) and columns are dates (report_date)
            for data_item, row in df.iterrows():
                for report_date, value in row.items():
                    # Check if the date has a 'date()' method (Pandas Timestamp)
                    if hasattr(report_date, 'date'):
                        date_val = report_date.date()
                    else:
                        date_val = report_date  # Should be datetime.date object or similar

                    if pd.notna(value):
                        data_tuple = (
                            ticker_id,
                            date_val,
                            data_item,
                            # Assuming values are typically large integers
                            int(value)
                        )
                        try:
                            cursor.execute(insert_query, data_tuple)
                        except Error as e:
                            print(
                                f"❌ MySQL Error inserting {data_item} on {date_val} for {table_name}: {e}")

            connection.commit()
            print(f"✅ {statement_name} data committed successfully.")

    except Error as e:
        print(f"❌ MySQL Error in store_financials_mysql: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed for financials.")

# --- END OF UPDATE store_data.py ---
