from dataclasses import dataclass, field
from datetime import datetime

from PIL import Image

from asistente_guiador.core.models import (
    GlobalScreenState,
    GuidanceResponse,
    IntentResult,
    VisualElementResult,
)


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
    global_screen_state: GlobalScreenState = field(default_factory=GlobalScreenState)

    def record_interaction(self, user_text: str, assistant_text: str) -> None:
        """Registra un turno en el historial corto (máximo 6 turnos para eficiencia)."""
        self.conversation_history.append({"user": user_text, "assistant": assistant_text})
        if len(self.conversation_history) > 6:
            self.conversation_history.pop(0)

    def update_screenshot(self, image: Image.Image) -> None:
        """Actualiza el frame en memoria."""
        self.last_screenshot = image
        self.last_screenshot_timestamp = datetime.now()

    def update_screen_context(
        self,
        image: Image.Image,
        window_title: str,
        has_changed: bool,
    ) -> None:
        """Actualiza la captura viva y los metadatos de ventana en el estado global."""
        self.update_screenshot(image)
        self.global_screen_state.active_window_title = window_title
        self.global_screen_state.has_structural_change = has_changed
        self.global_screen_state.last_updated = datetime.now()

    def update_screen_summary(self, summary: str, detected_app: str | None = None) -> None:
        """Actualiza el resumen semántico global tras la inferencia de visión."""
        self.global_screen_state.screen_summary = summary
        if detected_app and detected_app != "Unknown":
            self.global_screen_state.active_application = detected_app
            self.active_application = detected_app
        self.global_screen_state.has_structural_change = False
        self.global_screen_state.last_updated = datetime.now()
