"""Inicialización del módulo de dominio de AI Tutor."""

from src.ai_tutor.dependencies import get_ai_tutor_service
from src.ai_tutor.service import AiTutorService

__all__ = ["AiTutorService", "get_ai_tutor_service"]
