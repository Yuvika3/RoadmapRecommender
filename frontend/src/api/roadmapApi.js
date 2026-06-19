export async function generateRoadmap(payload) {
  const response = await fetch(
    "http://localhost:8000/generate-roadmap",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    }
  );

  if (!response.ok) {
    throw new Error("Failed to generate roadmap");
  }

  return response.json();
}

export async function fetchRoadmaps() {
  const response = await fetch("http://localhost:8000/roadmaps");
  if (!response.ok) {
    throw new Error("Failed to fetch roadmap history");
  }
  return response.json();
}

export async function fetchRoadmap(id) {
  const response = await fetch(`http://localhost:8000/roadmaps/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch roadmap details");
  }
  return response.json();
}

export async function deleteRoadmap(id) {
  const response = await fetch(`http://localhost:8000/roadmaps/${id}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error("Failed to delete roadmap");
  }
  return response.json();
}