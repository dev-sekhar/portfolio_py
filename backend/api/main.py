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
from ..data_core.data_access import fetch_ticker_id, fetch_financial_statement, fetch_latest_price, fetch_price_history

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
        # If ticker not found, try to ingest it.
        ingestion_success = ingest_ticker_data(
            symbol.upper(), 'all', days=365, interval='1d')

        # If ingestion fails, we can't proceed.
        if not ingestion_success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker '{symbol.upper()}' not found and could not be ingested. Please check the symbol."
            )

        # Try fetching the ID again after successful ingestion.
        ticker_id = fetch_ticker_id(symbol.upper())
        if ticker_id is None:
            # This case is unlikely if ingestion was successful, but good to have.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ticker '{symbol.upper()}' was ingested but could not be found in the database."
            )

    return ticker_id

# 4. API Endpoints


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Financial Data Hub API is running. Access /docs for endpoints."}


@app.get("/api/v1/ticker/{symbol}/prices", tags=["Price Data"], dependencies=[Depends(verify_api_key)])
async def get_price_history_endpoint(
    ticker_id: Annotated[int, Depends(get_ticker_id)],
    days: int = 365
) -> list[dict[str, Any]]:
    """Retrieves historical price data for the last N days."""
    if days < 1 or days > 7300:  # Approx. 20 years
        raise HTTPException(
            status_code=400, detail="Days must be between 1 and 7300.")

    price_data = fetch_price_history(ticker_id, days)
    if not price_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No historical price data found for this ticker.")

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
    ticker_id: Annotated[int, Depends(get_ticker_id)],
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Income Statement reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")

    data = fetch_financial_statement(ticker_id, 'income_stmt', quarters)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No income statement data found.")

    return data


@app.get("/api/v1/ticker/{symbol}/balance-sheet", tags=["Financials"], dependencies=[Depends(verify_api_key)])
async def get_balance_sheet_endpoint(
    ticker_id: Annotated[int, Depends(get_ticker_id)],
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Balance Sheet reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")

    data = fetch_financial_statement(ticker_id, 'balance_sheet', quarters)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No balance sheet data found.")

    return data


@app.get("/api/v1/ticker/{symbol}/cash-flow", tags=["Financials"], dependencies=[Depends(verify_api_key)])
async def get_cash_flow_endpoint(
    ticker_id: Annotated[int, Depends(get_ticker_id)],
    quarters: int = 4
) -> list[dict[str, Any]]:
    """Retrieves the last N quarterly Cash Flow reports."""

    if quarters < 1 or quarters > 12:
        raise HTTPException(
            status_code=400, detail="Quarters must be between 1 and 12.")

    data = fetch_financial_statement(ticker_id, 'cash_flow', quarters)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No cash flow data found.")

    return data

# Note on Corporate Actions:
# Endpoints for Dividends/Splits will be similar to the above,
# using a dedicated fetch_corporate_actions function in data_access.py.