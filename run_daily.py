import mysql.connector
from mysql.connector import Error
import subprocess
import sys
import os


def fetch_tickers_from_db(host, db, user, password):
    try:
        conn = mysql.connector.connect(
            host=host,
            database=db,
            user=user,
            password=password,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM tickers")
        tickers = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tickers
    except Error as e:
        print(f"DB connection error: {e}")
        sys.exit(1)


def run_portfolio_for_ticker(ticker):
    cmd = [sys.executable, "portfolio.py", "--ticker",
           ticker, "--days", "2", "--interval", "1d"]
    try:
        subprocess.run(cmd, check=True)
        print(f"Finished processing {ticker}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {ticker}: {e}")


def main():
    # These should match your .env file or environment variables in GitHub Actions
    host = os.getenv('DB_HOST', '127.0.0.1')
    database = os.getenv('DB_NAME', 'portfolio')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'root')

    tickers = fetch_tickers_from_db(host, database, user, password)
    print(f"Tickers fetched: {tickers}")

    for ticker in tickers:
        print(f"Processing ticker: {ticker}")
        run_portfolio_for_ticker(ticker)


if __name__ == "__main__":
    main()
