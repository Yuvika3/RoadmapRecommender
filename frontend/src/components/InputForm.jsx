import { useState } from "react";
import { generateRoadmap } from "../api/roadmapApi";

export default function InputForm({ setRoadmap }) {
  const [formData, setFormData] = useState({
    goal: "",
    current_level: "beginner",
    hours_per_week: ""
  });

  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      setLoading(true);
      setRoadmap(null); // Clear previous output on new submission

      const data = await generateRoadmap({
        goal: formData.goal,
        current_level: formData.current_level,
        hours_per_week: Number(formData.hours_per_week)
      });

      setRoadmap(data);
    } catch (error) {
      console.error(error);
      alert("Failed to generate roadmap. Please make sure Ollama is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card animated-fade-in">
      <form onSubmit={handleSubmit}>
        <h2>Define Your Learning Goal</h2>
        <p style={{ color: "#94a3b8", fontSize: "0.95rem", marginBottom: "0.5rem" }}>
          Provide details about your objectives, current skill level, and schedule to build your tailored learning path.
        </p>

        <div className="form-group">
          <label htmlFor="goal">Goal / Career Objective</label>
          <input
            id="goal"
            type="text"
            name="goal"
            placeholder="e.g. Backend Developer, Data Scientist..."
            value={formData.goal}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="current_level">Current Experience Level</label>
          <select
            id="current_level"
            name="current_level"
            value={formData.current_level}
            onChange={handleChange}
            required
          >
            <option value="beginner">Beginner (No prior experience)</option>
            <option value="intermediate">Intermediate (Some foundation)</option>
            <option value="advanced">Advanced (Looking to specialize)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="hours_per_week">Weekly Time Commitment (Hours)</label>
          <input
            id="hours_per_week"
            type="number"
            name="hours_per_week"
            min="1"
            max="168"
            placeholder="e.g. 10"
            value={formData.hours_per_week}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? (
            <>
              <div className="spinner"></div>
              <span>Crafting path...</span>
            </>
          ) : (
            "Generate Personal Roadmap"
          )}
        </button>
      </form>
    </div>
  );
}