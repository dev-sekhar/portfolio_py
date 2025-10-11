from langchain.tools import BaseTool
import yfinance as yf

class StockNewsTool(BaseTool):
    name: str = "Stock News"
    description: str = "Useful for fetching the latest news headlines for a given stock symbol."

    def _run(self, symbol: str) -> str:
        """Use the tool."""
        try:
            ticker = yf.Ticker(symbol)
            news_items = ticker.news
            if news_items:
                headlines = []
                for item in news_items:
                    if 'content' in item and 'title' in item['content']:
                        headlines.append(f"- {item['content']['title']}")
                if headlines:
                    return f"Latest news for {symbol}:\n" + "\n".join(headlines)
                else:
                    return f"No news with titles found for {symbol}."
            else:
                return f"Could not retrieve news for {symbol}."
        except Exception as e:
            return f"An error occurred: {e}"

    async def _arun(self, symbol: str) -> str:
        """Use the tool asynchronously."""
        # This is a placeholder for asynchronous implementation
        return self._run(symbol)
