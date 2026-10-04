import asyncio
import logging

from PyQt6.QtWidgets import QApplication

from asistente_guiador.ai.providers.groq_provider import GroqLLMProvider
from asistente_guiador.ai.providers.vision_provider import OpenRouterVisionProvider
from asistente_guiador.audio.recorder import VoiceActivityRecorder
from asistente_guiador.audio.stt import GroqWhisperSTTProvider
from asistente_guiador.audio.tts import PiperTTSProvider
from asistente_guiador.audio.wakeword import WakeWordAudioListener
from asistente_guiador.config.settings import Settings
from asistente_guiador.core.coordinator import AssistanceCoordinator
from asistente_guiador.overlay.fallback_hint import FloatingHintBanner
from asistente_guiador.overlay.overlay import TransparentOverlayWidget
from asistente_guiador.ui.tray import SystemTrayManager
from asistente_guiador.vision.capture import MSSScreenCapturer

logger = logging.getLogger("asistente_guiador")


class AsistenteApp:
    """Aplicación principal que conecta GUI (PyQt6), audio, orquestador y bucle de escucha."""

    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.settings = Settings()
        self._running = True

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

        # Detector de Wake Word dedicado: sólo activa la escucha cuando se dice la palabra clave
        self.wake_detector = WakeWordAudioListener(
            stt_provider=self.stt,
            wake_word=self.settings.wake_word,
        )

        # 3. Orquestador
        self.coordinator = AssistanceCoordinator(
            llm_provider=self.llm,
            vision_provider=self.vision,
            screen_capturer=self.capturer,
            tts_provider=self.tts,
        )

        # Inicializar contexto de pantalla base
        self.coordinator.initialize_visual_context()

        # 4. Bandeja del sistema (Tray)
        self.tray = SystemTrayManager(self)
        self.tray.show()

    async def process_user_query(self, user_query: str) -> None:
        """Ejecuta un ciclo de consulta, pinta el halo y muestra apoyo textual."""
        logger.info(f"Procesando: '{user_query}'")
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
            self.fallback_banner.show_hint(resp.spoken_text, duration_ms=8000)

    async def listen_loop(self) -> None:
        """
        Bucle continuo en segundo plano:
        1. Permanece en espera escuchando localmente por el Wake Word ("hey asistente").
        2. ÚNICAMENTE tras detectar el Wake Word, abre la escucha activa para capturar la orden.
        3. Procesa la petición como un turno de chat continuo.
        4. Regresa inmediatamente al bucle de espera por el siguiente Wake Word.
        """
        logger.info(
            f"🎤 Bucle de escucha continuo activo. Di '{self.settings.wake_word}' para activar."
        )

        while self._running:
            if not self.wake_detector.is_listening():
                await asyncio.sleep(0.5)
                continue

            # 1. Esperar exclusivamente a que se pronuncie la palabra de activación
            wake_detected = await self.wake_detector.wait_for_wake_word()
            if not wake_detected or not self.wake_detector.is_listening():
                continue

            # 2. Indicar que el asistente está escuchando activamente
            logger.info("✨ ¡Wake word detectado! Escuchando orden del usuario...")
            self.fallback_banner.show_hint("🎤 Te escucho, dime qué necesitas...", duration_ms=3000)
            await self.tts.speak("Sí, te escucho.")

            # 3. Grabar la intervención del usuario con tolerancia a pausas (1.8s)
            audio_bytes = await self.recorder.record_phrase_async()
            if not audio_bytes:
                logger.info("No se capturó audio tras la activación.")
                continue

            # 4. Transcribir orden a texto
            text = await self.stt.transcribe(audio_bytes)
            if not text or len(text.strip()) < 2:
                logger.info("Transcripción vacía o inaudible.")
                continue

            logger.info(f"🗣️ Pregunta del usuario recibida: '{text}'")

            # 5. Procesar consulta en la sesión continua de chat
            await self.process_user_query(text)
