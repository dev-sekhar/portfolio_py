import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import pandas as pd

load_dotenv()


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
    host = os.getenv('DB_HOST', 'host')
    port = int(os.getenv('DB_PORT', 'port'))
    database = os.getenv('DB_NAME', 'portfolio')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'password')

    try:
        print("🔄 Connecting to MySQL database...")
        connection = mysql.connector.connect(
            host=host, port=port,
            database=database, user=user,
            password=password, auth_plugin='mysql_native_password',
            connection_timeout=5
        )

        if connection.is_connected():
            print(f"✅ Connected to database '{database}'")
        else:
            print("❌ Failed to connect")
            return

        cursor = connection.cursor()

        # tickers table
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
        if row:
            ticker_id = row[0]
            cursor.execute(
                "UPDATE tickers SET exchange=%s WHERE id=%s", (exchange, ticker_id))
        else:
            cursor.execute(
                "INSERT INTO tickers (symbol, exchange) VALUES (%s, %s)", (ticker_symbol, exchange))
            ticker_id = cursor.lastrowid
        connection.commit()

        # stock_prices table
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
            ON DUPLICATE KEY UPDATE open=VALUES(open), high=VALUES(high),
            low=VALUES(low), close=VALUES(close), adj_close=VALUES(adj_close),
            volume=VALUES(volume), last_modified=CURRENT_TIMESTAMP, exchange=VALUES(exchange)
        """

        print(f"📊 Inserting/updating {len(stock_data)} price records")
        for idx, row in stock_data.iterrows():
            record_date = idx.date() if hasattr(idx, 'date') else idx
            try:
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
                cursor.execute(insert_query, data_tuple)
            except Exception as ex:
                print(f"❌ Error inserting price for {record_date}: {ex}")
        connection.commit()
        print("✅ Stock price data committed")

    except Error as e:
        print(f"❌ MySQL Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed")


def store_corporate_actions_mysql(corp_action_data, ticker_symbol, exchange, action_type='dividend'):
    connection = None
    host = os.getenv('DB_HOST', 'host')
    port = int(os.getenv('DB_PORT', 'port'))
    database = os.getenv('DB_NAME', 'portfolio')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')

    try:
        print("🔄 Connecting to MySQL database for corporate actions...")
        connection = mysql.connector.connect(
            host=host, port=port,
            database=database, user=user,
            password=password, auth_plugin='mysql_native_password',
            connection_timeout=5
        )

        if not connection.is_connected():
            print("❌ Failed to connect")
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

        # corporate_actions table
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
            INSERT INTO corporate_actions (ticker_id, action_type, action_date, cash_amount, description)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE cash_amount=VALUES(cash_amount),
                description=VALUES(description), created_at=CURRENT_TIMESTAMP
        """

        print(
            f"📊 Inserting/updating {len(corp_action_data)} corporate actions")
        for action_date, amount in corp_action_data.items():
            try:
                data_tuple = (
                    ticker_id,
                    action_type,
                    action_date,
                    float(amount) if pd.notna(amount) else None,
                    None
                )
                cursor.execute(insert_query, data_tuple)
            except Exception as ex:
                print(
                    f"❌ Error inserting corporate action on {action_date}: {ex}")
        connection.commit()
        print("✅ Corporate actions committed")

    except Error as e:
        print(f"❌ MySQL Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 MySQL connection closed")
