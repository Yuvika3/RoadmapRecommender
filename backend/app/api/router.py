from fastapi import APIRouter
from app.api.routes import roadmap

api_router = APIRouter()
api_router.include_router(roadmap.router, prefix="/api", tags=["roadmap"])
