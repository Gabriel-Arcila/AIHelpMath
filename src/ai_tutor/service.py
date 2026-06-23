class AiTutorService:
    """Servicio de inteligencia artificial para tutorías matemáticas.

    Encapsula la lógica de integración con modelos de lenguaje y generación
    de explicaciones de problemas.
    """

    def __init__(self) -> None:
        """Inicializa el servicio AiTutorService."""
        pass

    def explain_problem(self, problem: str, level: str) -> str:
        """Genera una explicación detallada del problema según el nivel del usuario.

        Args:
            problem (str): El problema matemático a explicar.
            level (str): El nivel de conocimiento del usuario (ej. 'PRINCIPIANTE').

        Returns:
            str: Explicación y resolución simulada del problema.
        """
        return (
            f"Esta es una explicación simulada para el problema: "
            f"'{problem}' a nivel {level}."
        )
