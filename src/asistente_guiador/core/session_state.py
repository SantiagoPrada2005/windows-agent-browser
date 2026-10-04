from dataclasses import dataclass, field
from datetime import datetime

from PIL import Image

from asistente_guiador.core.models import GuidanceResponse, IntentResult, VisualElementResult


@dataclass
class SessionState:
    """Estado temporal en memoria de la sesión activa del usuario."""

    active_application: str = "Unknown"
    last_screenshot: Image.Image | None = None
    last_screenshot_timestamp: datetime | None = None
    last_intent: IntentResult | None = None
    last_guidance: GuidanceResponse | None = None
    last_visual_result: VisualElementResult | None = None
    conversation_history: list[dict] = field(default_factory=list)

    def record_interaction(self, user_text: str, assistant_text: str) -> None:
        """Registra un turno en el historial corto (máximo 6 turnos para eficiencia)."""
        self.conversation_history.append({"user": user_text, "assistant": assistant_text})
        if len(self.conversation_history) > 6:
            self.conversation_history.pop(0)

    def update_screenshot(self, image: Image.Image) -> None:
        """Actualiza el frame en memoria."""
        self.last_screenshot = image
        self.last_screenshot_timestamp = datetime.now()
