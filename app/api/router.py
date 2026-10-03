from fastapi import APIRouter

from app.api.questions.router import router as questions_router
from app.api.topics.router import router as topics_router

api_router = APIRouter()

api_router.include_router(topics_router)
api_router.include_router(questions_router)
