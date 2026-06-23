"""Esquemas Pydantic para el dominio de AI Tutor."""

from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    """Esquema para solicitar la explicación de un problema matemático.

    Args:
        problem (str): El problema matemático a explicar.
        level (str): El nivel del estudiante (ej. 'PRINCIPIANTE', 'INTERMEDIO').
    """

    problem: str = Field(..., description="El problema matemático a explicar")
    level: str = Field(
        ..., description="El nivel de conocimiento o tipo de explicación requerida"
    )


class ExplainResponse(BaseModel):
    """Esquema para la respuesta de la explicación de un problema matemático.

    Args:
        explanation (str): Explicación del problema matemático.
    """

    explanation: str = Field(
        ..., description="La explicación detallada y paso a paso del problema"
    )
