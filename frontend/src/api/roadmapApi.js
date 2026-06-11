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