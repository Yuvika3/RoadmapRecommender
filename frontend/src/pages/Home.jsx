import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import InputForm from "../components/InputForm";
import RoadmapOutput from "../components/RoadmapOutput";
import { fetchRoadmaps, fetchRoadmap, deleteRoadmap } from "../api/roadmapApi";

export default function Home() {
  const [roadmap, setRoadmap] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("form"); // "form" or "roadmap"
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Fetch history list when component mounts
  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    try {
      setLoadingHistory(true);
      const data = await fetchRoadmaps();
      setHistory(data);
    } catch (error) {
      console.error("Failed to load roadmap history", error);
    } finally {
      setLoadingHistory(false);
    }
  }

  async function handleSelectHistory(id) {
    try {
      const details = await fetchRoadmap(id);
      setRoadmap(details);
      setActiveTab("roadmap");
    } catch (error) {
      console.error("Failed to load roadmap details", error);
      alert("Failed to load roadmap details.");
    }
  }

  async function handleDeleteHistory(e, id) {
    e.stopPropagation(); // Prevent clicking item
    if (!confirm("Are you sure you want to delete this roadmap?")) {
      return;
    }
    try {
      await deleteRoadmap(id);
      if (roadmap && roadmap.id === id) {
        setRoadmap(null);
        setActiveTab("form");
      }
      loadHistory();
    } catch (error) {
      console.error("Failed to delete roadmap", error);
      alert("Failed to delete roadmap.");
    }
  }

  function handleRoadmapGenerated(newRoadmap) {
    if (!newRoadmap) {
      setRoadmap(null);
      setActiveTab("form");
      return;
    }

    setRoadmap(newRoadmap);
    setActiveTab("roadmap");
    loadHistory(); // Refresh history sidebar
  }

  return (
    <div className="app-container">
      <Navbar />
      <div className="main-layout">
        <aside className="sidebar">
          <button 
            className="new-roadmap-btn"
            onClick={() => {
              setRoadmap(null);
              setActiveTab("form");
            }}
          >
            + Create New Path
          </button>
          
          <div className="sidebar-section-title">Saved Paths</div>
          
          {loadingHistory ? (
            <div className="sidebar-status">
              Loading saved paths...
            </div>
          ) : history.length === 0 ? (
            <div className="sidebar-status empty">No saved roadmaps yet.</div>
          ) : (
            <ul className="history-list">
              {history.map((item) => (
                <li 
                  key={item.id}
                  className={`history-item ${roadmap && roadmap.id === item.id && activeTab === "roadmap" ? "active" : ""}`}
                  onClick={() => handleSelectHistory(item.id)}
                >
                  <div className="history-item-content">
                    <span className="history-item-goal">{item.goal}</span>
                    <span className="history-item-meta">
                      {item.current_level} • {item.hours_per_week}h/wk
                    </span>
                  </div>
                  <button 
                    className="history-delete-btn"
                    onClick={(e) => handleDeleteHistory(e, item.id)}
                    title="Delete path"
                  >
                    &times;
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>
        
        <main className="content-area">
          {activeTab === "form" ? (
            <div className="container">
              <InputForm setRoadmap={handleRoadmapGenerated} />
            </div>
          ) : (
            roadmap && (
              <div className="container">
                <button 
                  className="editorial-back-btn"
                  onClick={() => setActiveTab("form")}
                >
                  &larr; Create Another Path
                </button>
                <RoadmapOutput key={roadmap.id} roadmap={roadmap} />
              </div>
            )
          )}
        </main>
      </div>
    </div>
  );
}
