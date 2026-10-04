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
from asistente_guiador.vision.window_detector import (
    ActiveWindowDetector,
    get_default_window_detector,
)

logger = logging.getLogger(__name__)


class AssistanceCoordinator:
    """
    Orquestador principal del flujo del asistente con:
    - Contexto visual global continuo de pantalla siempre presente.
    - Manejo de sesión tipo chat continuo.
    - Inferencia adaptativa para ahorrar llamadas remotas.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        vision_provider: VisionProvider,
        screen_capturer: ScreenCapturer,
        tts_provider: TTSProvider,
        session_state: SessionState | None = None,
        change_detector: ScreenChangeDetector | None = None,
        window_detector: ActiveWindowDetector | None = None,
    ):
        self.llm = llm_provider
        self.vision = vision_provider
        self.capturer = screen_capturer
        self.tts = tts_provider
        self.session = session_state or SessionState()
        self.change_detector = change_detector or ScreenChangeDetector()
        self.window_detector = window_detector or get_default_window_detector()
        self._initial_screen_context: str | None = None

    def initialize_visual_context(self) -> None:
        """Captura inicial de pantalla para fijar el contexto de la aplicación activa."""
        try:
            initial_screen = self.capturer.capture_active_screen()
            window_title = self.window_detector.get_active_window_title()
            self.session.update_screen_context(
                image=initial_screen,
                window_title=window_title,
                has_changed=True,
            )
            self._initial_screen_context = (
                f"Resolución de pantalla: {initial_screen.width}x{initial_screen.height}. "
                f"Ventana activa inicial: '{window_title}'."
            )
            logger.info(
                f"Contexto visual inicial de pantalla registrado (Ventana: '{window_title}')."
            )
        except Exception as e:
            logger.warning(f"No se pudo inicializar contexto visual: {e}")

    async def handle_user_request(self, user_text: str) -> GuidanceResponse:
        """Punto de entrada cuando se transcribe una orden del usuario tras el wake word."""
        logger.info(f"Procesando petición en sesión de chat: '{user_text}'")

        # 0. Asegurar contexto inicial si no se hizo previamente
        if self.session.last_screenshot is None:
            self.initialize_visual_context()
        else:
            current_win = self.window_detector.get_active_window_title()
            if current_win != self.session.global_screen_state.active_window_title:
                self.session.global_screen_state.active_window_title = current_win

        # 1. Manejo inmediato de repetición
        clean_text = unicodedata.normalize("NFD", user_text)
        clean_text = "".join(c for c in clean_text if unicodedata.category(c) != "Mn").lower()

        if "repite" in clean_text or "otra vez" in clean_text:
            if self.session.last_guidance:
                response = self.session.last_guidance
                await self.tts.speak(response.spoken_text)
                return response

        # 2. Clasificación de intención informada con el estado de pantalla continuo
        intent_result: IntentResult = await self.llm.classify_intent(
            user_text,
            session_context=self.session.conversation_history,
            screen_state=self.session.global_screen_state,
        )
        self.session.last_intent = intent_result

        # 3. Flujo condicional: ¿Requiere localización visual de elemento?
        visual_result: VisualElementResult | None = None
        current_screen: Image.Image = (
            self.session.last_screenshot or self.capturer.capture_active_screen()
        )
        has_changed = self.change_detector.has_significant_change(current_screen)

        if intent_result.requires_visual_context and intent_result.target:
            if (
                not has_changed
                and self.session.last_visual_result
                and self.session.last_visual_result.target.lower() == intent_result.target.lower()
            ):
                logger.info("Pantalla sin cambios relevantes: Reutilizando coordenadas en caché.")
                visual_result = self.session.last_visual_result
            else:
                logger.info("Invocando proveedor de visión para localizar elemento objetivo.")
                visual_result = await self.vision.analyze_screen(
                    current_screen,
                    target_description=intent_result.target,
                    context=(
                        f"Ventana activa: {self.session.global_screen_state.active_window_title}. "
                        f"Resumen de pantalla: {self.session.global_screen_state.screen_summary}"
                    ),
                )
                self.session.update_screenshot(current_screen)
                self.session.last_visual_result = visual_result
                if visual_result.application and visual_result.application != "Unknown":
                    self.session.active_application = visual_result.application
                    self.session.global_screen_state.active_application = visual_result.application
        else:
            self.session.update_screenshot(current_screen)

        # 4. Generación de respuesta guiada manteniendo el contexto de pantalla continuo
        response: GuidanceResponse = await self.llm.generate_response(
            intent=intent_result,
            visual_result=visual_result,
            conversation_history=self.session.conversation_history,
            initial_context=self._initial_screen_context,
            screen_state=self.session.global_screen_state,
        )

        # 5. Guardar en memoria de sesión tipo chat y reproducir verbalmente
        self.session.last_guidance = response
        self.session.record_interaction(user_text, response.spoken_text)
        await self.tts.speak(response.spoken_text)

        return response
