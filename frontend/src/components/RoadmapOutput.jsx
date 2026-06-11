export default function RoadmapOutput({ roadmap }) {
  if (!roadmap) return null;

  // Map source to display text and badge class
  const sourceMap = {
    ollama: { text: "AI Optimized", className: "badge badge-ollama" },
    ollama_fallback: { text: "AI Formatted Fallback", className: "badge badge-ollama-fallback" },
    fallback: { text: "Rule-Based Fallback", className: "badge badge-fallback" }
  };

  const currentSource = sourceMap[roadmap.source] || { text: roadmap.source, className: "badge" };

  return (
    <div className="animated-fade-in" style={{ marginTop: "1rem" }}>
      <div className="glass-card">
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          flexWrap: "wrap", 
          gap: "10px", 
          marginBottom: "1.5rem", 
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)", 
          paddingBottom: "1rem" 
        }}>
          <h2 style={{ marginBottom: 0 }}>Your Learning Roadmap</h2>
          <span className={currentSource.className}>{currentSource.text}</span>
        </div>

        {roadmap.explanation && (
          <div className="explanation-card animated-fade-in">
            <h4 style={{ color: "#a5b4fc", fontSize: "0.95rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
              Advisor Tips & Strategy
            </h4>
            <p>{roadmap.explanation}</p>
          </div>
        )}

        {roadmap.scores && (
          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.06)", paddingBottom: "0.5rem" }}>
              Skill Metrics Profile
            </h3>
            <div className="skills-grid">
              {Object.entries(roadmap.scores).map(([skill, score]) => (
                <div key={skill} className="skill-card">
                  <div className="skill-header">
                    <span className="skill-title">{skill}</span>
                  </div>

                  <div className="score-row">
                    <div className="score-label">
                      <span>Relevance</span>
                      <span>{Math.round(score.skill_relevance_score * 100)}%</span>
                    </div>
                    <div className="progress-bar-bg">
                      <div
                        className="progress-bar-fill fill-relevance"
                        style={{ width: `${score.skill_relevance_score * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="score-row">
                    <div className="score-label">
                      <span>Difficulty</span>
                      <span>{Math.round(score.difficulty_score * 100)}%</span>
                    </div>
                    <div className="progress-bar-bg">
                      <div
                        className="progress-bar-fill fill-difficulty"
                        style={{ width: `${score.difficulty_score * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="score-row">
                    <div className="score-label">
                      <span>Time Feasibility</span>
                      <span>{Math.round(score.time_feasibility_score * 100)}%</span>
                    </div>
                    <div className="progress-bar-bg">
                      <div
                        className="progress-bar-fill fill-feasibility"
                        style={{ width: `${score.time_feasibility_score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {roadmap.roadmap && (
          <div style={{ marginTop: "2rem" }}>
            <h3 style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.06)", paddingBottom: "0.5rem", marginBottom: "1.5rem" }}>
              Weekly Study Plan
            </h3>
            <div className="roadmap-timeline">
              {Object.entries(roadmap.roadmap).map(([week, tasks]) => (
                <div key={week} className="week-card">
                  <h4 className="week-title">
                    <span className="week-badge">{week}</span>
                  </h4>
                  <ul className="task-list">
                    {tasks.map((task, index) => (
                      <li key={index} className="task-item">
                        <input
                          type="checkbox"
                          className="task-checkbox"
                          id={`task-${week}-${index}`}
                        />
                        <label className="task-text" htmlFor={`task-${week}-${index}`}>
                          {task}
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}