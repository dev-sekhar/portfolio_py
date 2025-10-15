from langchain.tools import BaseTool
import yfinance as yf
from typing import List, Dict, Any

class StockNewsTool(BaseTool):
    name: str = "Stock News"
    description: str = "Useful for fetching the latest news headlines for a given stock symbol. Returns a list of news articles."

    def _run(self, symbol: str) -> List[Dict[str, Any]]:
        """Use the tool."""
        try:
            ticker = yf.Ticker(symbol)
            news_items = ticker.news
            if news_items:
                return news_items
            else:
                return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    async def _arun(self, symbol: str) -> List[Dict[str, Any]]:
        """Use the tool asynchronously."""
        return self._run(symbol)
