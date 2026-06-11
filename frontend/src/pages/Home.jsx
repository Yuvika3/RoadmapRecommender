import Navbar from "../components/Navbar";
import InputForm from "../components/InputForm";
import RoadmapOutput from "../components/RoadmapOutput";
import { useState } from "react";

export default function Home() {
  const [roadmap, setRoadmap] = useState(null);

  return (
    <>
      <Navbar />
      <div className="container">
        <InputForm setRoadmap={setRoadmap} />
        {roadmap && <RoadmapOutput roadmap={roadmap} />}
      </div>
    </>
  );
}