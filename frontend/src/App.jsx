import { useState, useEffect } from "react";
import "./App.css";
import FinancialTable from "./components/FinancialTable";
import PriceTable from "./components/PriceTable"; // Import the new component
import { fetchFinancialData, fetchPriceHistory } from "./api/financialsApi";

// --- CONFIGURATION ---
// IMPORTANT: This key is for demonstration only. In production, this would be managed by a login system.
const CLIENT_API_KEY = "d3f8a9c2-7e4b-4b1a-9f6a-8c2e9f1a1234";
// --- END CONFIGURATION ---

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [quarters, setQuarters] = useState(4);
  const [days, setDays] = useState(365);
  const [dataType, setDataType] = useState("all");
  const [incomeData, setIncomeData] = useState(null);
  const [balanceData, setBalanceData] = useState(null);
  const [cashData, setCashData] = useState(null);
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    if (!ticker) return;

    setLoading(true);
    setError(null);
    setIncomeData(null);
    setBalanceData(null);
    setCashData(null);
    setPriceData(null);

    try {
      if (dataType === "financials" || dataType === "all") {
        const [income, balance, cash] = await Promise.all([
          fetchFinancialData(
            ticker,
            "income-statement",
            CLIENT_API_KEY,
            quarters
          ),
          fetchFinancialData(ticker, "balance-sheet", CLIENT_API_KEY, quarters),
          fetchFinancialData(ticker, "cash-flow", CLIENT_API_KEY, quarters),
        ]);
        setIncomeData(income);
        setBalanceData(balance);
        setCashData(cash);
      }

      if (dataType === "price" || dataType === "all") {
        const price = await fetchPriceHistory(ticker, CLIENT_API_KEY, days);
        setPriceData(price);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Financial Data Hub Portal</h1>
      <p>
        Consuming the FastAPI Backend (frontend\src\api on
        http://127.0.0.1:8000) using React.
      </p>
      <div
        style={{
          marginBottom: "20px",
          border: "1px solid #ccc",
          padding: "20px",
          borderRadius: "5px",
        }}
      >
        <h2>Settings</h2>
        <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
          <label>
            Ticker Symbol:
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              style={{ marginLeft: "10px", padding: "5px" }}
            />
          </label>
          <label>
            Data Type:
            <select
              value={dataType}
              onChange={(e) => setDataType(e.target.value)}
              style={{ marginLeft: "10px", padding: "5px" }}
            >
              <option value="all">All</option>
              <option value="financials">Financials</option>
              <option value="price">Price</option>
            </select>
          </label>
          <button
            onClick={fetchData}
            disabled={loading}
            style={{ padding: "10px 20px", cursor: "pointer" }}
          >
            {loading ? "Loading..." : "Fetch & Analyze"}
          </button>
        </div>
        <div
          style={{
            display: "flex",
            gap: "20px",
            alignItems: "center",
            marginTop: "10px",
          }}
        >
          <label>
            Quarters:
            <input
              type="number"
              value={quarters}
              onChange={(e) =>
                setQuarters(Math.min(12, Math.max(1, Number(e.target.value))))
              }
              min="1"
              max="12"
              style={{ marginLeft: "10px", padding: "5px", width: "60px" }}
              disabled={dataType === "price"}
            />
          </label>
          <label>
            Days (for Price History):
            <input
              type="number"
              value={days}
              onChange={(e) =>
                setDays(Math.min(7300, Math.max(1, Number(e.target.value))))
              }
              min="1"
              max="7300"
              style={{ marginLeft: "10px", padding: "5px", width: "80px" }}
              disabled={dataType === "financials"}
            />
          </label>
        </div>
      </div>

      {error && (
        <div
          style={{
            color: "red",
            border: "1px solid red",
            padding: "10px",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "40px",
          marginTop: "40px",
        }}
      >
        {priceData && (
          <div style={{ gridColumn: "1 / -1" }}>
            <PriceTable data={priceData} title="Price Data" />
          </div>
        )}
        {incomeData && (
          <div style={{ gridColumn: "1 / -1" }}>
            <FinancialTable
              data={incomeData}
              title="Quarterly Income Statement"
            />
          </div>
        )}
        {balanceData && (
          <div style={{ gridColumn: "1 / -1" }}>
            <FinancialTable
              data={balanceData}
              title="Quarterly Balance Sheet"
            />
          </div>
        )}
        {cashData && (
          <div style={{ gridColumn: "1 / -1" }}>
            <FinancialTable data={cashData} title="Quarterly Cash Flow" />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
