import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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
