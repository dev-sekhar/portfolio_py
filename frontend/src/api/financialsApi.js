// --- START OF FILE frontend/src/api/financialsApi.js ---
// A simple service wrapper to manage communication with the backend.

const API_BASE_URL = "http://127.0.0.1:8000/api/v1"; 

/**
 * Calls the Financial Data Hub API to retrieve data for a given endpoint.
 * @param {string} ticker - Stock ticker symbol.
 * @param {string} endpoint - API endpoint suffix (e.g., 'income-statement').
 * @param {string} apiKey - Client's API Key.
 * @param {number} quarters - Number of quarters to retrieve.
 * @returns {Promise<Array<Object>>} - An array of data records.
 */
export const fetchFinancialData = async (ticker, endpoint, apiKey, quarters = 4) => {
    const url = `${API_BASE_URL}/ticker/${ticker}/${endpoint}?quarters=${quarters}`;
    
    // 1. Build the Request
    const requestOptions = {
        method: 'GET',
        headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, requestOptions);

        // 2. Handle Errors (Authentication, Rate Limits, 404)
        if (response.status === 401) {
            throw new Error("Authentication Failed: Invalid or missing API Key.");
        }
        if (response.status === 429) {
            const error = await response.json();
            throw new Error(`Rate Limit Exceeded: ${error.detail}`);
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API Error (${response.status}): ${error.detail || 'Failed to fetch data'}`);
        }

        // 3. Return Data
        return await response.json();

    } catch (error) {
        console.error("Fetch Error:", error);
        throw error;
    }
};

/**
 * Fetches historical price data for a given ticker.
 * @param {string} ticker - Stock ticker symbol.
 * @param {string} apiKey - Client's API Key.
 * @param {number} days - Number of days to retrieve.
 * @returns {Promise<Array<Object>>} - An array of price data records.
 */
export const fetchPriceHistory = async (ticker, apiKey, days = 365) => {
    const url = `${API_BASE_URL}/ticker/${ticker}/prices?days=${days}`;
    
    const requestOptions = {
        method: 'GET',
        headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, requestOptions);

        if (response.status === 401) {
            throw new Error("Authentication Failed: Invalid or missing API Key.");
        }
        if (response.status === 429) {
            const error = await response.json();
            throw new Error(`Rate Limit Exceeded: ${error.detail}`);
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API Error (${response.status}): ${error.detail || 'Failed to fetch data'}`);
        }

        return await response.json();

    } catch (error) {
        console.error("Fetch Error:", error);
        throw error;
    }
};
// --- END OF FILE frontend/src/api/financialsApi.js ---