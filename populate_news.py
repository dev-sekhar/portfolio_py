#!/usr/bin/env python3
import sys
sys.path.append('backend')

from backend.tools.stock_news_tool import StockNewsTool
from backend.data_core.store.store_data import store_stock_news_mysql

def populate_news_for_ticker(ticker):
    print(f"Fetching news for {ticker}...")
    
    news_tool = StockNewsTool()
    news = news_tool._run(ticker)
    
    if news:
        store_stock_news_mysql(news, ticker)
        print(f"Stored {len(news)} news articles for {ticker}")
        return True
    else:
        print(f"No news found for {ticker}")
        return False

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "ORCL"]
    
    for ticker in tickers:
        try:
            populate_news_for_ticker(ticker)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
        print("-" * 40)