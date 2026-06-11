export default function Navbar() {
  return (
    <nav style={{
      padding: "1.25rem 2rem",
      background: "rgba(11, 15, 25, 0.85)",
      backdropFilter: "blur(16px)",
      WebkitBackdropFilter: "blur(16px)",
      borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
      position: "sticky",
      top: 0,
      zIndex: 100,
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <div style={{
          width: "32px",
          height: "32px",
          borderRadius: "8px",
          background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontWeight: "bold",
          fontSize: "1.1rem",
          color: "white",
          boxShadow: "0 0 15px rgba(99, 102, 241, 0.3)"
        }}>
          R
        </div>
        <h2 style={{ 
          fontSize: "1.3rem", 
          fontWeight: "700", 
          margin: 0, 
          background: "linear-gradient(to right, #ffffff, #c7d2fe)", 
          WebkitBackgroundClip: "text", 
          WebkitTextFillColor: "transparent" 
        }}>
          Roadmap Recommender
        </h2>
      </div>
      
      <div>
        <span style={{ 
          fontSize: "0.8rem", 
          color: "#475569", 
          fontWeight: "600", 
          background: "rgba(255,255,255,0.03)", 
          padding: "4px 8px", 
          borderRadius: "6px",
          border: "1px solid rgba(255,255,255,0.05)"
        }}>
          V1.1
        </span>
      </div>
    </nav>
  );
}