# Proposed Architecture

The proposed architecture is a Microservice-Oriented Monorepo using distinct layers for data, services, and presentation.

## Proposed Project Structure & Architecture

We will organize the repository around three top-level directories: backend, frontend, and config.

### Architecture Rationale

1. Monorepo (/): Houses all project code (BE, FE) under a single version control system.
2. backend/data*core (Library Layer): This is your Data Access Layer. It contains the fundamental logic (fetch*, store\_, db_connection) that the API, CLI, and ETL tools all import and reuse. This prevents code duplication.
3. backend/api (Service Layer - Financial Hub): This is the REST API you will build (using FastAPI). It handles authentication, routing, and serves the pre-processed data by calling the data_core.
4. backend/pricing_service (Independent Microservice): This is separate because pricing logic changes frequently and should not impact the main data API. It would run as its own service, and the frontend/billing system would call it separately.
5. backend/tools (Utility Layer): This houses one-off scripts and command-line interfaces (CLIs) for maintenance and data ingestion.
6. frontend/ (Presentation Layer): This will be the research portal GUI.

# Detailed Project Structure

Below is the suggested folder structure and how your existing files map to it.
code
Code
.
├── backend/
│ ├── api/ # 1. Main Financial Data API (FastAPI)
│ │ ├── **init**.py
│ │ ├── main.py # (Was api_app.py in previous plan) API routes and authentication.
│ │ ├── requirements.txt # FastAPI, Uvicorn, etc.
│ │
│ ├── data_core/ # 2. Reusable Data Access Layer (Library)
│ │ ├── **init**.py # Makes the directory a Python package
│ │ ├── db_connection.py # (Existing) Database connection credentials
│ │ ├── data_access.py # (New) Consolidated functions to read data from DB for the API/Tools.
│ │ ├── fetch/
│ │ │ ├── **init**.py
│ │ │ ├── fetch_price_data.py # (Existing)
│ │ │ ├── fetch_dividend_data.py # (Existing)
│ │ │ ├── fetch_splits_data.py # (Existing)
│ │ │ └── fetch_financials_data.py # (New)
│ │ ├── store/
│ │ │ ├── **init**.py
│ │ │ └── store_data.py # (Existing) Logic for MySQL writes (prices, actions, financials)
│ │ └── requirements.txt # yfinance, pandas, mysql-connector-python
│ │
│ ├── pricing_service/ # 3. Independent Pricing Microservice
│ │ ├── main.py # FastAPI/Flask app for pricing/billing logic (e.g., usage checks)
│ │ └── requirements.txt # Dedicated requirements for this service
│ │
│ └── tools/ # 4. CLI and Utility Scripts
│ ├── **init**.py
│ ├── portfolio_cli.py # (Refactored from portfolio.py) Main data ingestion CLI
│ ├── cleanup_db.py # (Existing)
│ ├── export_data.py # (New) Script for B2B ETL/Bulk export
│ └── display_data.py # (Existing) CLI display logic (only used by portfolio_cli.py)
│
├── frontend/ # 5. Research Portal (e.g., React/Vue/Angular)
│ ├── src/
│ ├── public/
│ ├── package.json # Frontend dependencies
│ └── ...
│
├── config/
│ ├── docker-compose.yml # For orchestrating the FE, BE, Pricing, and MySQL
│ └── setup.sql # Initial DB setup script
│
├── .gitignore
├── .env # Environment variables (DB creds, API Keys)
