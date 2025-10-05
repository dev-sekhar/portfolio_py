import mysql.connector
from mysql.connector import Error
import pandas as pd


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
        WHERE table_schema = DATABASE() AND table_name = %s AND constraint_name = %s AND constraint_type = 'FOREIGN KEY'
    """, (table_name, fk_name))
    return cursor.fetchone()[0] > 0


def store_stock_data_mysql(stock_data, ticker_symbol, exchange, host, database, user, password):
    connection = None
    try:
        print("🔄 Attempting to connect to MySQL database...")
        connection = mysql.connector.connect(
            host=host,
            port=3306,
            database=database,
            user=user,
            password=password,
            auth_plugin='mysql_native_password',
            connection_timeout=5
        )

        if connection.is_connected():
            print(f"✅ Connected to MySQL database '{database}'")
        else:
            print("❌ Failed to connect to MySQL database.")
            return

        cursor = connection.cursor()

        print("🛠️ Ensuring 'tickers' table exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(16) UNIQUE NOT NULL,
                exchange VARCHAR(16)
            )
        """)
        connection.commit()
        print("✅ 'tickers' table ensured.")

        print(f"🔄 Inserting or updating ticker '{ticker_symbol}'...")
        cursor.execute(
            "SELECT id FROM tickers WHERE symbol = %s", (ticker_symbol,))
        row = cursor.fetchone()
        if row:
            ticker_id = row[0]
            cursor.execute(
                "UPDATE tickers SET exchange=%s WHERE id=%s", (exchange, ticker_id))
            print(f"🔁 Updated ticker '{ticker_symbol}'.")
        else:
            cursor.execute(
                "INSERT INTO tickers (symbol, exchange) VALUES (%s, %s)", (ticker_symbol, exchange))
            ticker_id = cursor.lastrowid
            print(f"🆕 Inserted ticker '{ticker_symbol}' with id {ticker_id}.")
        connection.commit()

        print("🛠️ Ensuring 'stock_prices' table exists...")
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
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("✅ 'stock_prices' table ensured.")

        cursor.execute(
            "SHOW INDEX FROM stock_prices WHERE Key_name = 'PRIMARY'")
        primary_index_info = cursor.fetchall()
        if primary_index_info:
            primary_columns = [row[4] for row in primary_index_info]
            if set(primary_columns) != {'ticker_id', 'date'}:
                cursor.execute("ALTER TABLE stock_prices DROP PRIMARY KEY")
                connection.commit()
                print("⚠️ Dropped existing primary key from stock_prices.")

        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT ticker_id, date, COUNT(*) AS c
                FROM stock_prices
                GROUP BY ticker_id, date
                HAVING c > 1
            ) AS duplicates
        """)
        duplicates = cursor.fetchone()[0]
        if duplicates == 0:
            try:
                cursor.execute(
                    "ALTER TABLE stock_prices ADD PRIMARY KEY (ticker_id, date)")
                connection.commit()
                print("✅ Composite primary key (ticker_id, date) added.")
            except Error as e:
                print(f"⚠️ Failed to add composite primary key: {e}")
        else:
            print(
                f"⚠️ Cannot add composite primary key due to {duplicates} duplicate rows.")

        print("🔗 Checking foreign key constraint...")
        if not foreign_key_exists(cursor, 'stock_prices', 'fk_ticker'):
            try:
                cursor.execute("""
                    ALTER TABLE stock_prices
                    ADD CONSTRAINT fk_ticker FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
                """)
                connection.commit()
                print("✅ Foreign key constraint 'fk_ticker' added.")
            except Error as e:
                print(f"❌ Failed to add foreign key: {e}")
        else:
            print("✅ Foreign key 'fk_ticker' already exists.")

        adj_close_col = 'Adj Close' if 'Adj Close' in stock_data.columns else 'Close'

        insert_query = """
            INSERT INTO stock_prices (ticker_id, date, open, high, low, close, adj_close, volume, exchange)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open=VALUES(open),
                high=VALUES(high),
                low=VALUES(low),
                close=VALUES(close),
                adj_close=VALUES(adj_close),
                volume=VALUES(volume),
                last_modified=CURRENT_TIMESTAMP,
                exchange=VALUES(exchange)
        """

        print(f"📊 Inserting/updating {len(stock_data)} stock price records...")

        for idx, row in stock_data.iterrows():
            record_date = idx.date() if hasattr(idx, 'date') else idx
            try:
                open_ = float(row['Open']) if pd.notna(row['Open']) else None
                high = float(row['High']) if pd.notna(row['High']) else None
                low = float(row['Low']) if pd.notna(row['Low']) else None
                close = float(row['Close']) if pd.notna(row['Close']) else None
                adj_close = float(row[adj_close_col]) if pd.notna(
                    row[adj_close_col]) else None
                volume = int(row['Volume']) if pd.notna(row['Volume']) else 0

                data_tuple = (
                    ticker_id,
                    record_date,
                    open_,
                    high,
                    low,
                    close,
                    adj_close,
                    volume,
                    exchange
                )
                cursor.execute(insert_query, data_tuple)
                print(f"✔️ Inserted/updated record for {record_date}")

            except Error as e:
                print(f"❌ MySQL Error for {record_date}: {e}")
            except Exception as ex:
                print(f"❌ General Error for {record_date}: {ex}")

        connection.commit()
        print("✅ All stock data committed successfully.")

    except Error as e:
        print(f"❌ MySQL Connection/Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed.")
