# This is the core implementation of the B2B Ticker Fundamentals API. It handles routing, authentication, and error handling.
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
import re
from typing import Annotated, Any

from ..tools.portfolio_cli import ingest_ticker_data

# Import Data Access Layer
from ..data_core.data_access import fetch_ticker_id, fetch_financial_statement, fetch_latest_price, fetch_price_history, fetch_corporate_actions, fetch_stock_news

load_dotenv()
# The Master API Key from the environment file
MASTER_API_KEY = os.getenv("MASTER_API_KEY", "DEFAULT_MASTER_KEY_SECRET")

# 1. API Setup
app = FastAPI(
    title="B2B Financial Data Hub API",
    description="Programmatic access to normalized Price and Quarterly Financials.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Authentication Dependency
# We'll use a simple Header check for initial B2B MVP


async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """
    Verifies the API key passed in the X-API-Key header.
    In a production system, this would check a database of client keys 
    and track usage.
    """
    if x_api_key is None or x_api_key != MASTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Please provide a valid X-API-Key header.",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    return x_api_key

# 3. Middleware for Ticker ID


def get_ticker_id(symbol: str) -> int:
    """Helper dependency to look up the ticker ID and handle 404 errors."""
    if not re.match(r"^[A-Z0-9\.\-]+$", symbol):
        raise HTTPException(
            status_code=400, detail="Invalid ticker symbol format.")

    ticker_id = fetch_ticker_id(symbol.upper())
    if ticker_id is None:
        # If ticker not found, try to ingest basic ticker info first
        from ..data_core.store.store_data import store_stock_data_mysql
        from ..data_core.db_connection import get_db_connection
        import yfinance as yf
        
        try:
            ticker_obj = yf.Ticker(symbol.upper())
            info = ticker_obj.info
            if 'symbol' in info:
                # Add ticker to database
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT IGNORE INTO tickers (symbol, exchange) VALUES (%s, %s)", 
                        (symbol.upper(), info.get('exchange', 'Unknown'))
                    )
                    connection.commit()
                    cursor.close()
                    connection.close()
                    
                    # Get the ticker_id
                    ticker_id = fetch_ticker_id(symbol.upper())
        except Exception as e:
            print(f"Error adding ticker {symbol}: {e}")
            
        if ticker_id is None:
            # Last resort: try basic ingestion
            try:
                success = ingest_ticker_data(symbol.upper(), 'price', days=1, interval='1d')
                if success:
                    ticker_id = fetch_ticker_id(symbol.upper())
            except:
                pass
                
        if ticker_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker '{symbol.upper()}' not found. Please check the symbol."
            )

    return ticker_id

# 4. API Endpoints


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Financial Data Hub API is running. Access /docs for endpoints."}


@app.get("/api/v1/ticker/{symbol}/prices", tags=["Price Data"], dependencies=[Depends(verify_api_key)])
async def get_price_history_endpoint(
    symbol: str,
    days: int = 365
) -> list[dict[str, Any]]:
    """Retrieves historical price data for the last N days."""
    if days < 1 or days > 7300:  # Approx. 20 years
        raise HTTPException(
            status_code=400, detail="Days must be between 1 and 7300.")
    
    ticker_id = get_ticker_id(symbol)

    price_data = fetch_price_history(ticker_id, days)
    if not price_data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'price', days=days, interval='1d')
            if success:
                price_data = fetch_price_history(ticker_id, days)
        except:
            pass
        if not price_data:
            return []

    return price_data


@app.get("/api/v1/ticker/{symbol}/prices/latest", tags=["Price Data"], dependencies=[Depends(verify_api_key)])
async def get_latest_price_endpoint(
    ticker_id: Annotated[int, Depends(get_ticker_id)]
) -> dict[str, Any]:
    """Retrieves the latest recorded price data for the ticker."""

    price_data = fetch_latest_price(ticker_id)
    if price_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No price data found for this ticker.")

    return price_data


@app.get("/api/v1/ticker/{symbol}/income-statement", tags=["Financials"], dependencies=[Depends(verify_api_key)])
async def get_income_statement_endpoint(
    symbol: str,
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Income Statement reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")
    
    ticker_id = get_ticker_id(symbol)

    data = fetch_financial_statement(ticker_id, 'income_stmt', quarters)
    if not data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'financials')
            if success:
                data = fetch_financial_statement(ticker_id, 'income_stmt', quarters)
        except:
            pass
        if not data:
            return []

    return data


@app.get("/api/v1/ticker/{symbol}/balance-sheet", tags=["Financials"], dependencies=[Depends(verify_api_key)])
async def get_balance_sheet_endpoint(
    symbol: str,
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Balance Sheet reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")
    
    ticker_id = get_ticker_id(symbol)

    data = fetch_financial_statement(ticker_id, 'balance_sheet', quarters)
    if not data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'financials')
            if success:
                data = fetch_financial_statement(ticker_id, 'balance_sheet', quarters)
        except:
            pass
        if not data:
            return []

    return data


@app.get("/api/v1/ticker/{symbol}/cash-flow", tags=["Financials"], dependencies=[Depends(verify_api_key)])
async def get_cash_flow_endpoint(
    symbol: str,
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Cash Flow reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")
    
    ticker_id = get_ticker_id(symbol)

    data = fetch_financial_statement(ticker_id, 'cash_flow', quarters)
    if not data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'financials')
            if success:
                data = fetch_financial_statement(ticker_id, 'cash_flow', quarters)
        except:
            pass
        if not data:
            return []

    return data

@app.get("/api/v1/ticker/{symbol}/dividends", tags=["Corporate Actions"], dependencies=[Depends(verify_api_key)])
async def get_dividends_endpoint(
    symbol: str
) -> list[dict[str, Any]]:
    """Retrieves all dividend history for a ticker."""
    ticker_id = get_ticker_id(symbol)
    data = fetch_corporate_actions(ticker_id, 'dividend')
    if not data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'dividend')
            if success:
                data = fetch_corporate_actions(ticker_id, 'dividend')
        except:
            pass
        if not data:
            return []
    return data


@app.get("/api/v1/ticker/{symbol}/splits", tags=["Corporate Actions"], dependencies=[Depends(verify_api_key)])
async def get_splits_endpoint(
    symbol: str
) -> list[dict[str, Any]]:
    """Retrieves all stock split history for a ticker."""
    ticker_id = get_ticker_id(symbol)
    data = fetch_corporate_actions(ticker_id, 'split')
    if not data:
        try:
            success = ingest_ticker_data(symbol.upper(), 'split')
            if success:
                data = fetch_corporate_actions(ticker_id, 'split')
        except:
            pass
        if not data:
            return []
    return data


# Note on Corporate Actions:
# Endpoints for Dividends/Splits will be similar to the above,
# using a dedicated fetch_corporate_actions function in data_access.py.

@app.get("/api/v1/ticker/{symbol}/news", tags=["News"], dependencies=[Depends(verify_api_key)])
async def get_stock_news_endpoint(
    symbol: str,
    limit: int = 10
) -> list[dict[str, Any]]:
    """Retrieves the latest news articles for a ticker."""
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400, detail="Limit must be between 1 and 100.")

    ticker_id = get_ticker_id(symbol)
    news_data = fetch_stock_news(ticker_id, limit)
    if not news_data:
        # Try to fetch and store news data
        try:
            success = ingest_ticker_data(symbol.upper(), 'news')
            if success:
                news_data = fetch_stock_news(ticker_id, limit)
        except Exception as e:
            print(f"Error ingesting news data for {symbol}: {e}")
        
        if not news_data:
            return []  # Return empty array instead of 404

    return news_data