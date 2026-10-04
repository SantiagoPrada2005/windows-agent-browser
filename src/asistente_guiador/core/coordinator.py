import logging
import unicodedata

from PIL import Image

from asistente_guiador.core.interfaces import (
    LLMProvider,
    ScreenCapturer,
    TTSProvider,
    VisionProvider,
)
from asistente_guiador.core.models import (
    GuidanceResponse,
    IntentResult,
    VisualElementResult,
)
from asistente_guiador.core.session_state import SessionState
from asistente_guiador.vision.change_detector import ScreenChangeDetector

logger = logging.getLogger(__name__)


class AssistanceCoordinator:
    """Orquestador principal del flujo del asistente con inferencia adaptativa."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        vision_provider: VisionProvider,
        screen_capturer: ScreenCapturer,
        tts_provider: TTSProvider,
        session_state: SessionState | None = None,
        change_detector: ScreenChangeDetector | None = None,
    ):
        self.llm = llm_provider
        self.vision = vision_provider
        self.capturer = screen_capturer
        self.tts = tts_provider
        self.session = session_state or SessionState()
        self.change_detector = change_detector or ScreenChangeDetector()

    async def handle_user_request(self, user_text: str) -> GuidanceResponse:
        """Punto de entrada cuando se transcribe una orden de voz del usuario."""
        logger.info(f"Procesando petición del usuario: '{user_text}'")

        # 1. Manejo inmediato de repetición
        clean_text = unicodedata.normalize("NFD", user_text)
        clean_text = "".join(c for c in clean_text if unicodedata.category(c) != "Mn").lower()

        if "repite" in clean_text or "otra vez" in clean_text:
            if self.session.last_guidance:
                response = self.session.last_guidance
                await self.tts.speak(response.spoken_text)
                return response

        # 2. Clasificación de intención con LLM rápido
        history_context = (
            str(self.session.conversation_history[-2:])
            if self.session.conversation_history
            else None
        )
        intent_result: IntentResult = await self.llm.classify_intent(
            user_text,
            session_context=history_context,
        )
        self.session.last_intent = intent_result

        # 3. Flujo condicional: ¿Requiere contexto visual?
        visual_result: VisualElementResult | None = None
        if intent_result.requires_visual_context and intent_result.target:
            current_screen: Image.Image = self.capturer.capture_active_screen()
            has_changed = self.change_detector.has_significant_change(current_screen)

            if (
                not has_changed
                and self.session.last_visual_result
                and self.session.last_visual_result.target.lower() == intent_result.target.lower()
            ):
                logger.info("Pantalla sin cambios relevantes: Reutilizando contexto en caché.")
                visual_result = self.session.last_visual_result
            else:
                logger.info("Cambio detectado: Invocando proveedor de visión.")
                visual_result = await self.vision.analyze_screen(
                    current_screen,
                    target_description=intent_result.target,
                )
                self.session.update_screenshot(current_screen)
                self.session.last_visual_result = visual_result

        # 4. Generación de respuesta guiada adaptada
        response: GuidanceResponse = await self.llm.generate_response(
            intent=intent_result,
            visual_result=visual_result,
        )

        # 5. Actualización de estado y reproducción verbal
        self.session.last_guidance = response
        self.session.record_interaction(user_text, response.spoken_text)
        await self.tts.speak(response.spoken_text)

        return response
