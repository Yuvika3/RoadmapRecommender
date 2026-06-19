from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import roadmap
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup SQLite tables on startup
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for local dev flexibility
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, GET, etc
    allow_headers=["*"],
)
app.include_router(roadmap.router)