import React from 'react';

const CorporateActionsTable = ({ data, title }) => {
    if (!data || data.length === 0) {
        return <div>No data available for {title}.</div>;
    }

    const headers = Object.keys(data[0]);

    return (
        <div>
            <h2>{title}</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr>
                        {headers.map(header => (
                            <th key={header} style={{ border: '1px solid #ccc', padding: '8px', textAlign: 'left' }}>{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, index) => (
                        <tr key={index}>
                            {headers.map(header => (
                                <td key={header} style={{ border: '1px solid #ccc', padding: '8px' }}>{row[header]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CorporateActionsTable;