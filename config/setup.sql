-- SQL script to set up the initial database schema for the portfolio project.

-- Create the 'tickers' table to store stock symbols and basic info.
CREATE TABLE IF NOT EXISTS tickers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE COMMENT 'Stock ticker symbol',
    exchange VARCHAR(50) COMMENT 'Stock exchange where the ticker is listed'
) COMMENT='Stores unique stock ticker symbols and their exchanges.';

-- Create the 'stock_prices' table for daily price data.
CREATE TABLE IF NOT EXISTS stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_id INT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(18, 4),
    high DECIMAL(18, 4),
    low DECIMAL(18, 4),
    close DECIMAL(18, 4),
    adj_close DECIMAL(18, 4),
    volume BIGINT,
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE,
    UNIQUE KEY (ticker_id, date)
) COMMENT='Stores daily stock price and volume data.';

-- Create the 'corporate_actions' table for dividends and splits.
CREATE TABLE IF NOT EXISTS corporate_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_id INT NOT NULL,
    action_date DATE NOT NULL,
    action_type VARCHAR(20) NOT NULL COMMENT 'e.g., dividend, split',
    cash_amount DECIMAL(18, 4) COMMENT 'Dividend amount per share',
    stock_ratio VARCHAR(20) COMMENT 'Stock split ratio, e.g., 2:1',
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
) COMMENT='Stores corporate actions like dividends and stock splits.';

-- Create the 'stock_news' table.
CREATE TABLE IF NOT EXISTS stock_news (
    uuid VARCHAR(36) PRIMARY KEY,
    ticker_id INT,
    title TEXT,
    publisher VARCHAR(255),
    link TEXT,
    provider_publish_time DATETIME,
    type VARCHAR(50),
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
) COMMENT='Stores news articles related to stocks.';

-- Create tables for quarterly financial statements.
CREATE TABLE IF NOT EXISTS financials_income_stmt_quarterly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_id INT NOT NULL,
    report_date DATE NOT NULL,
    data_item VARCHAR(255) NOT NULL,
    value DECIMAL(20, 4),
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE,
    UNIQUE KEY (ticker_id, report_date, data_item)
) COMMENT='Stores quarterly income statement data.';

CREATE TABLE IF NOT EXISTS financials_balance_sheet_quarterly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_id INT NOT NULL,
    report_date DATE NOT NULL,
    data_item VARCHAR(255) NOT NULL,
    value DECIMAL(20, 4),
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE,
    UNIQUE KEY (ticker_id, report_date, data_item)
) COMMENT='Stores quarterly balance sheet data.';

CREATE TABLE IF NOT EXISTS financials_cash_flow_quarterly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker_id INT NOT NULL,
    report_date DATE NOT NULL,
    data_item VARCHAR(255) NOT NULL,
    value DECIMAL(20, 4),
    FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE,
    UNIQUE KEY (ticker_id, report_date, data_item)
) COMMENT='Stores quarterly cash flow statement data.';
