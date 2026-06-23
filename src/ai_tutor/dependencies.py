from src.ai_tutor.service import AiTutorService


def get_ai_tutor_service() -> AiTutorService:
    """Proveedor del servicio de AI Tutor para inyección de dependencias de FastAPI.

    Returns:
        AiTutorService: Instancia de AiTutorService.
    """
    return AiTutorService()
