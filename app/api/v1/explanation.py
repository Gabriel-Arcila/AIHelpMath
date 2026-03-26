from fastapi import APIRouter
from app.schemas.explanation import ExplanationRequest, ExplanationResponse
from app.services.ai_tutor import ai_tutor_service

router = APIRouter()

@router.post("/", response_model=ExplanationResponse)
def explain_math_problem(request: ExplanationRequest):
    """
    Recibe un problema matemático y devuelve una explicación paso a paso.
    """
    explanation_text = ai_tutor_service.explain_problem(request.problem, request.level)
    
    return ExplanationResponse(
        explanation=explanation_text,
        steps=["Paso 1: Identificar...", "Paso 2: Resolver..."]
    )
