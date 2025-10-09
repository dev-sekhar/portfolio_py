// --- START OF FILE frontend/src/components/FinancialTable.jsx ---
import React, { useMemo } from 'react';
// import './FinancialTable.css'; // Uncomment this and create the CSS file for styling

// Helper function for formatting large numbers
const formatValue = (value) => {
    if (value === null || value === undefined) return '';
    const num = Number(value);
    if (isNaN(num)) return '';

    if (Math.abs(num) >= 1_000_000_000) {
        return `${(num / 1_000_000_000).toFixed(2)}B`;
    }
    if (Math.abs(num) >= 1_000_000) {
        return `${(num / 1_000_000).toFixed(2)}M`;
    }
    return num.toLocaleString();
};

/**
 * Renders a financial statement, pivoting the data for a clean row/column view.
 * @param {Object} props - Component props.
 * @param {Array<Object>} props.data - Flat array of {report_date, data_item, value} from the API.
 * @param {string} props.title - Title for the statement (e.g., "Income Statement").
 */
const FinancialTable = ({ data, title }) => {
    
    // Memoize the data transformation for performance
    const { headers, rows } = useMemo(() => {
        if (!data || data.length === 0) return { headers: [], rows: [] };

        const allDates = [...new Set(data.map(item => item.report_date))].sort().reverse();
        const allItems = [...new Set(data.map(item => item.data_item))];
        const pivotMap = {};

        // 1. Build a map: {data_item: {date1: value, date2: value, ...}}
        data.forEach(item => {
            if (!pivotMap[item.data_item]) {
                pivotMap[item.data_item] = {};
            }
            pivotMap[item.data_item][item.report_date] = item.value;
        });

        // 2. Format the data for table rendering
        const tableRows = allItems.map(itemKey => {
            const row = { key: itemKey, values: {} };
            allDates.forEach(date => {
                const value = pivotMap[itemKey][date];
                row.values[date] = formatValue(value);
            });
            return row;
        });

        return { headers: ['Metric', ...allDates], rows: tableRows };
    }, [data]);

    if (rows.length === 0) return <div>No data available for {title}.</div>;

    return (
        <div className="financial-table-container" style={{overflowX: 'auto'}}>
            <h3>{title}</h3>
            {/* Added inline style for mobile-friendliness: allow horizontal scroll */}
            <table style={{width: '100%', minWidth: '700px', borderCollapse: 'collapse'}}>
                <thead>
                    <tr>
                        {headers.map(header => <th key={header} style={{textAlign: 'left', padding: '10px', borderBottom: '2px solid #ccc', backgroundColor: '#f0f0f0'}}>{header.replace(/([A-Z])/g, ' $1').trim()}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, index) => (
                        <tr key={row.key} style={{borderBottom: '1px solid #eee'}}>
                            {/* Metric Name */}
                            <td style={{fontWeight: 'bold', padding: '10px'}}>{row.key.replace(/([A-Z])/g, ' $1').trim().replace(/([A-Z])([A-Z])([a-z])/g, '$1 $2$3')}</td> 
                            {/* Quarterly Values */}
                            {headers.slice(1).map(date => (
                                <td key={date} style={{padding: '10px', textAlign: 'right'}}>{row.values[date]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default FinancialTable;
// --- END OF FILE frontend/src/components/FinancialTable.jsx ---