from fetch_data import fetch_stock_data
from display_data import display_data
from store_data import store_stock_data_mysql


def main():
    ticker = input(
        "Enter the full stock ticker symbol (including suffix if any, e.g., AAPL or RELIANCE.NS): ").strip().upper()

    while True:
        days_str = input(
            "Enter number of trading days of historical data needed: ").strip()
        if days_str.isdigit() and int(days_str) > 0:
            days = int(days_str)
            break
        print("Please enter a valid positive integer for days.")

    interval_map = {"1": "1d", "2": "1wk", "3": "1mo"}
    while True:
        print("Choose data interval:\n1: Daily\n2: Weekly\n3: Monthly")
        interval_choice = input("Enter 1, 2, or 3: ").strip()
        if interval_choice in interval_map:
            interval = interval_map[interval_choice]
            break
        print("Please enter 1, 2, or 3.")

    stock_data = fetch_stock_data(ticker, days, interval)
    if stock_data.empty:
        print(
            f"No data returned for ticker {ticker}. Check symbol and try again.")
        return

    import yfinance as yf
    ticker_obj = yf.Ticker(ticker)
    exchange = ticker_obj.info.get('exchange', 'Unknown')

    display_data(stock_data, ticker, days, interval)

    host = '127.0.0.1'
    database = 'portfolio'
    user = 'root'
    password = 'root'

    store_stock_data_mysql(stock_data, ticker, exchange,
                           host, database, user, password)


if __name__ == "__main__":
    main()
