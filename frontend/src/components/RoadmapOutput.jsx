import { useState } from "react";

export default function RoadmapOutput({ roadmap }) {
  const [checkedTasks, setCheckedTasks] = useState(() => {
    if (roadmap && roadmap.id) {
      const saved = localStorage.getItem(`roadmap_tasks_${roadmap.id}`);
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          return {};
        }
      }
    }
    return {};
  });

  if (!roadmap) return null;

  // Handle checkbox changes
  const handleCheckboxChange = (week, index, isChecked) => {
    const key = `${week}-${index}`;
    setCheckedTasks((prev) => {
      const updated = { ...prev, [key]: isChecked };
      if (roadmap && roadmap.id) {
        localStorage.setItem(`roadmap_tasks_${roadmap.id}`, JSON.stringify(updated));
      }
      return updated;
    });
  };

  // Calculate percentage of tasks completed
  const totalTasks = roadmap.roadmap
    ? Object.values(roadmap.roadmap).reduce((sum, tasks) => sum + tasks.length, 0)
    : 0;

  const completedTasks = Object.keys(checkedTasks).filter(
    (key) => checkedTasks[key]
  ).length;

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="animated-fade-in" style={{ marginTop: "1rem" }}>
      <div className="glass-card">
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          flexWrap: "wrap", 
          gap: "15px", 
          marginBottom: "1.5rem", 
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)", 
          paddingBottom: "1.5rem" 
        }}>
          <h2 style={{ marginBottom: 0, fontSize: "2rem", textTransform: "capitalize" }}>
            {roadmap.goal}
          </h2>
          
          {totalTasks > 0 && (
            <div className="progress-badge">
              <span className="progress-label">Progress: {completionRate}%</span>
              <div className="mini-progress-bg">
                <div 
                  className="mini-progress-fill" 
                  style={{ width: `${completionRate}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {roadmap.explanation && (
          <div className="explanation-card animated-fade-in">
            <h4 style={{ color: "var(--accent)", fontSize: "0.95rem", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
              Curriculum Overview & Strategy
            </h4>
            <p>{roadmap.explanation}</p>
          </div>
        )}

        {roadmap.scores && (
          <div style={{ marginTop: "2.5rem" }}>
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
          <div style={{ marginTop: "2.5rem" }}>
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
                    {tasks.map((task, index) => {
                      const key = `${week}-${index}`;
                      const isChecked = !!checkedTasks[key];
                      return (
                        <li key={index} className="task-item">
                          <input
                            type="checkbox"
                            className="task-checkbox"
                            id={`task-${week}-${index}`}
                            checked={isChecked}
                            onChange={(e) => handleCheckboxChange(week, index, e.target.checked)}
                          />
                          <label className="task-text" htmlFor={`task-${week}-${index}`}>
                            {task}
                          </label>
                        </li>
                      );
                    })}
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