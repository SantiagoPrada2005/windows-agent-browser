import logging

from PyQt6.QtWidgets import QApplication

from asistente_guiador.ai.providers.groq_provider import GroqLLMProvider
from asistente_guiador.ai.providers.vision_provider import OpenRouterVisionProvider
from asistente_guiador.audio.recorder import VoiceActivityRecorder
from asistente_guiador.audio.stt import GroqWhisperSTTProvider
from asistente_guiador.audio.tts import PiperTTSProvider
from asistente_guiador.audio.wakeword import SimpleWakeWordDetector
from asistente_guiador.config.settings import Settings
from asistente_guiador.core.coordinator import AssistanceCoordinator
from asistente_guiador.overlay.fallback_hint import FloatingHintBanner
from asistente_guiador.overlay.overlay import TransparentOverlayWidget
from asistente_guiador.ui.tray import SystemTrayManager
from asistente_guiador.vision.capture import MSSScreenCapturer

logger = logging.getLogger("asistente_guiador")


class AsistenteApp:
    """Aplicación principal que conecta GUI (PyQt6), audio, orquestador y bandeja del sistema."""

    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.settings = Settings()

        # 1. Overlay y banner de degradación visual
        self.overlay = TransparentOverlayWidget()
        self.fallback_banner = FloatingHintBanner()

        screen = self.qapp.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.overlay.setGeometry(geo)
            self.overlay.show()

        # 2. Puertos de Audio, Visión y LLM
        self.llm = GroqLLMProvider(
            api_key=self.settings.groq_api_key,
            model=self.settings.groq_model,
        )
        self.vision = OpenRouterVisionProvider(
            api_key=self.settings.openrouter_api_key,
            model=self.settings.vision_model,
        )
        self.capturer = MSSScreenCapturer()
        self.tts = PiperTTSProvider()
        self.stt = GroqWhisperSTTProvider(api_key=self.settings.groq_api_key)
        self.recorder = VoiceActivityRecorder()
        self.wake_detector = SimpleWakeWordDetector(wake_word=self.settings.wake_word)

        # 3. Orquestador
        self.coordinator = AssistanceCoordinator(
            llm_provider=self.llm,
            vision_provider=self.vision,
            screen_capturer=self.capturer,
            tts_provider=self.tts,
        )

        # 4. Bandeja del sistema (Tray)
        self.tray = SystemTrayManager(self)
        self.tray.show()

    async def process_user_query(self, user_query: str) -> None:
        """Ejecuta un ciclo de consulta, pinta el halo y muestra apoyo textual."""
        logger.info(f"Usuario: '{user_query}'")
        resp = await self.coordinator.handle_user_request(user_query)

        # Si hay coordenadas fiables (Nivel A), dibujar halo
        if resp.visual_highlight:
            self.overlay.set_target_bbox(
                resp.visual_highlight,
                spatial_hint=resp.spatial_description,
            )
        else:
            self.overlay.clear_highlight()

        # Nivel B/C: mostrar banner de texto grande si aplica
        if resp.spoken_text:
            self.fallback_banner.show_hint(resp.spoken_text, duration_ms=7000)
