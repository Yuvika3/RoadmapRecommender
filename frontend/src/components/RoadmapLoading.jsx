const stages = [
  "Loading Profile",
  "Analyzing Skills",
  "Building Path",
  "Creating Timeline",
  "Finalizing Roadmap"
];

export default function RoadmapLoading() {
  return (
    <section className="roadmap-loading" aria-live="polite" aria-busy="true">
      <div className="roadmap-loading__header">
        <span className="roadmap-loading__eyebrow">Roadmap Engine</span>
        <h2>Building your learning path</h2>
        <p>
          Mapping your goal, skill level, and weekly commitment into a structured plan.
        </p>
      </div>

      <div className="roadmap-loading__timeline" role="list">
        {stages.map((stage, index) => (
          <div
            className="roadmap-loading__stage"
            style={{ "--stage-index": index }}
            role="listitem"
            key={stage}
          >
            <span className="roadmap-loading__node" aria-hidden="true">
              <span />
            </span>
            <span className="roadmap-loading__label">{stage}</span>
            <span className="roadmap-loading__status">Processing</span>
          </div>
        ))}
      </div>

      <div className="roadmap-loading__progress" aria-hidden="true">
        <span />
      </div>
    </section>
  );
}
