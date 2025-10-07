import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd  # <-- Added this import for display_financials


def display_data(stock_data, ticker_symbol, num_days, interval):
    print(f"Data contains {len(stock_data)} rows after slicing.")
    print(f"Date range: {stock_data.index.min()} to {stock_data.index.max()}")
    print(stock_data.head(num_days))

    ax = stock_data['Close'].plot(
        title=f"{ticker_symbol} Closing Price Last {num_days} Trading Days ({interval})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(5)
    plt.close()


def display_dividends(dividends, ticker_symbol):
    print(f"Dividends data contains {len(dividends)} records.")
    if not dividends.empty:
        print(
            f"Date range: {dividends.index.min()} to {dividends.index.max()}")
        print(dividends.head())

        ax = dividends.plot(
            kind='bar',
            title=f"{ticker_symbol} Dividend Payments",
            figsize=(10, 5),
            legend=False)

        ax.set_xlabel("Date")
        ax.set_ylabel("Dividend Amount")

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(5)
        plt.close()
    else:
        print(f"No dividend data to display for {ticker_symbol}.")


def display_splits(splits_series, ticker_symbol):
    if splits_series.empty:
        print(f"No split data found for ticker {ticker_symbol}.")
        return
    print(f"Stock Split History for {ticker_symbol}:")
    for split_date, split_ratio in splits_series.items():
        print(f" - {split_date.date()}: Split ratio {split_ratio}")


def display_financials(financials_data: dict, ticker_symbol: str):
    """
    Prints the quarterly financial statements to the terminal.
    """
    print(f"\n--- Quarterly Financials for {ticker_symbol} ---")

    for statement_name, df in financials_data.items():
        print(f"\n--- {statement_name.replace('_', ' ').title()} ---")
        if df is None or df.empty:
            print(f"No data available for {statement_name}.")
            continue

        # Transpose for better terminal readability (dates as columns)
        df_transposed = df.T

        # Format the numbers (e.g., in millions or billions for readability)
        # Assuming values are typically large integers/floats
        def format_value(x):
            if pd.isna(x):
                return ''
            # Use 'B' for billions, 'M' for millions
            if abs(x) >= 1_000_000_000:
                return f'{x / 1_000_000_000:,.2f}B'
            elif abs(x) >= 1_000_000:
                return f'{x / 1_000_000:,.2f}M'
            return f'{x:,.0f}'

        # Apply formatting to all non-index columns
        for col in df_transposed.columns:
            df_transposed[col] = df_transposed[col].apply(format_value)

        # Print the transposed, formatted DataFrame
        print(df_transposed)
