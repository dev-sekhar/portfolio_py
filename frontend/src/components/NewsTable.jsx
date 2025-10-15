const NewsTable = ({ newsData }) => {
  if (!newsData || newsData.length === 0) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        <h3>News</h3>
        <p>No news data available for this ticker.</p>
      </div>
    );
  }

  return (
    <div style={{ marginBottom: "40px" }}>
      <h3>Latest News</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
        {newsData.map((article, index) => (
          <div
            key={article.uuid || index}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "15px",
              backgroundColor: "#f9f9f9"
            }}
          >
            <h4 style={{ margin: "0 0 10px 0", fontSize: "16px" }}>
              <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                style={{ textDecoration: "none", color: "#0066cc" }}
              >
                {article.title}
              </a>
            </h4>
            <div style={{ fontSize: "14px", color: "#666", marginBottom: "5px" }}>
              <span><strong>Publisher:</strong> {article.publisher}</span>
              {article.provider_publish_time && (
                <span style={{ marginLeft: "15px" }}>
                  <strong>Published:</strong> {new Date(article.provider_publish_time).toLocaleDateString()}
                </span>
              )}
            </div>
            {article.type && (
              <div style={{ fontSize: "12px", color: "#888" }}>
                <strong>Type:</strong> {article.type}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default NewsTable;