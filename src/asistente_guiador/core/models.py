from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class GlobalScreenState(BaseModel):
    """Estado global continuo de la pantalla del usuario en memoria."""

    active_window_title: str = Field(
        default="Escritorio / Desconocido",
        description="Título de la ventana activa en primer plano",
    )
    active_application: str = Field(
        default="Desconocido",
        description="Nombre de la aplicación inferida o detectada",
    )
    screen_summary: str = Field(
        default="Pantalla base en espera de análisis.",
        description="Descripción semántica viva y comprensible de la interfaz actual",
    )
    last_updated: datetime = Field(default_factory=datetime.now)
    has_structural_change: bool = False


class IntentType(StrEnum):
    GENERAL_QUESTION = "general_question"
    LOCATE_ELEMENT = "locate_element"
    EXPLAIN_ACTION = "explain_action"
    GUIDE_MULTISTEP_TASK = "guide_multistep_task"
    CONFIRM_ACTION = "confirm_action"
    REPEAT_INSTRUCTION = "repeat_instruction"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


class ResponseStyle(StrEnum):
    SHORT_GUIDANCE = "short_guidance"
    CONCEPTUAL_EXPLANATION = "conceptual_explanation"
    CONFIRMATION = "confirmation"


class BoundingBox(BaseModel):
    """Coordenadas normalizadas relativas a la pantalla [0.0, 1.0]."""

    x: float = Field(..., ge=0.0, le=1.0, description="Coordenada X sup-izq normalizada")
    y: float = Field(..., ge=0.0, le=1.0, description="Coordenada Y sup-izq normalizada")
    width: float = Field(..., ge=0.0, le=1.0, description="Ancho normalizado")
    height: float = Field(..., ge=0.0, le=1.0, description="Alto normalizado")

    def to_pixel_coords(self, screen_width: int, screen_height: int) -> tuple[int, int, int, int]:
        """Convierte coordenadas normalizadas a píxeles enteros."""
        return (
            int(self.x * screen_width),
            int(self.y * screen_height),
            int(self.width * screen_width),
            int(self.height * screen_height),
        )


class IntentResult(BaseModel):
    """Resultado del clasificador/router de intención."""

    intent: IntentType
    target: str | None = Field(
        default=None,
        description="Elemento u objetivo mencionado por el usuario",
    )
    requires_visual_context: bool = Field(
        default=False,
        description="Si requiere análisis de screenshot",
    )
    response_style: ResponseStyle = Field(default=ResponseStyle.SHORT_GUIDANCE)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_query: str = Field(default="")


class VisualElementResult(BaseModel):
    """Resultado estructurado devuelto por el modelo de visión."""

    found: bool = Field(..., description="Si el elemento fue localizado con certeza")
    application: str = Field(
        default="Unknown",
        description="Aplicación identificada (e.g. Word, Bloc de Notas)",
    )
    target: str = Field(default="", description="Nombre del elemento buscado")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    bbox: BoundingBox | None = Field(
        default=None,
        description="Caja delimitadora normalizada si found=True",
    )
    spatial_description: str = Field(
        default="",
        description="Descripción espacial en lenguaje natural",
    )
    reason: str = Field(default="", description="Justificación o etiqueta observada")


class GuidanceResponse(BaseModel):
    """Respuesta consolidada para el usuario (voz y overlay)."""

    spoken_text: str
    visual_highlight: BoundingBox | None = None
    spatial_description: str | None = None
    needs_user_click: bool = True
