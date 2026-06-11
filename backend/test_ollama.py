import sys
import os
import json

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from llm.ollama_client import generate_roadmap_with_ollama, format_roadmap_with_ollama
from ml.scoring.scorer import score_skills

scores = score_skills("Backend Developer", "beginner", 10)
print("Scores:")
print(json.dumps(scores, indent=2))

print("\nCalling generate_roadmap_with_ollama...")
try:
    import requests
    from llm.ollama_client import OLLAMA_URL, MODEL
    
    # print available models
    tags = requests.get("http://localhost:11434/api/tags").json()
    print("Available models:")
    print(tags)

    res = generate_roadmap_with_ollama("Backend Developer", "beginner", 10, scores)
    print("Success!")
except Exception as e:
    print("Error:", e)


