from fastapi import APIRouter
from app.api.v1.endpoints import explanation

api_router = APIRouter()
api_router.include_router(explanation.router, prefix="/explanation", tags=["explanation"])
