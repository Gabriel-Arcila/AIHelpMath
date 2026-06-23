"""Mapeo de rutas para el dominio de AI Tutor."""

from fastapi import APIRouter, Depends, status

from src.ai_tutor.dependencies import get_ai_tutor_service
from src.ai_tutor.schemas import ExplainRequest, ExplainResponse
from src.ai_tutor.service import AiTutorService

router = APIRouter()


@router.post(
    "/explain",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explicar un problema matemático",
)
async def explain(
    request_data: ExplainRequest,
    service: AiTutorService = Depends(get_ai_tutor_service),
) -> ExplainResponse:
    """Genera una explicación paso a paso de un problema matemático
    adaptada al nivel del usuario.

    Args:
        request_data (ExplainRequest): El problema y el nivel del usuario.
        service (AiTutorService): Servicio de AI Tutor inyectado.

    Returns:
        ExplainResponse: La explicación estructurada del problema.
    """
    explanation_text = service.explain_problem(
        problem=request_data.problem,
        level=request_data.level,
    )
    return ExplainResponse(explanation=explanation_text)
