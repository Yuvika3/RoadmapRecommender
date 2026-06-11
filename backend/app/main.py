from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.routes import roadmap

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite frontend
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, GET, etc
    allow_headers=["*"],
)
app.include_router(roadmap.router)