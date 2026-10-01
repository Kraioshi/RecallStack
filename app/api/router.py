from fastapi import APIRouter

from app.api.topics.router import router as topics_router

api_router = APIRouter()

api_router.include_router(topics_router)
