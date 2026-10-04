import asyncio
import logging

from PyQt6.QtCore import QObject, pyqtSignal
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


class AppSignals(QObject):
    """
    Canal de señales Qt para comunicación segura entre hilos.
    Garantiza que cualquier modificación de UI se ejecute en el hilo principal.
    """

    show_hint = pyqtSignal(str, int)  # mensaje, duracion_ms
    show_highlight = pyqtSignal(object, str)  # BoundingBox, spatial_hint
    clear_highlight = pyqtSignal()


class AsistenteApp:
    """Aplicación principal que conecta GUI (PyQt6), audio, orquestador y bucle de escucha."""

    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.settings = Settings()
        self._running = True

        # 1. Overlay y banner de degradación visual en hilo principal
        self.overlay = TransparentOverlayWidget()
        self.fallback_banner = FloatingHintBanner()

        screen = self.qapp.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.overlay.setGeometry(geo)
            self.overlay.show()

        # 2. Canal de señales entre el hilo de audio y los widgets de interfaz
        self.signals = AppSignals()
        self.signals.show_hint.connect(self._handle_show_hint)
        self.signals.show_highlight.connect(self._handle_show_highlight)
        self.signals.clear_highlight.connect(self._handle_clear_highlight)

        # 3. Puertos de Audio, Visión y LLM
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
        self.recorder = VoiceActivityRecorder(
            silence_threshold_energy=self.settings.wake_word_energy_threshold
        )

        # Detector de Wake Word dedicado
        self.wake_detector = WakeWordAudioListener(
            stt_provider=self.stt,
            wake_word=self.settings.wake_word,
            energy_threshold=self.settings.wake_word_energy_threshold,
        )

        # 4. Orquestador
        self.coordinator = AssistanceCoordinator(
            llm_provider=self.llm,
            vision_provider=self.vision,
            screen_capturer=self.capturer,
            tts_provider=self.tts,
        )

        # Inicializar contexto de pantalla base
        self.coordinator.initialize_visual_context()

        # 5. Bandeja del sistema (Tray)
        self.tray = SystemTrayManager(self)
        self.tray.show()

    def _handle_show_hint(self, message: str, duration_ms: int) -> None:
        """Slot ejecutado en el hilo principal de Qt para mostrar banners."""
        self.fallback_banner.show_hint(message, duration_ms=duration_ms)

    def _handle_show_highlight(self, bbox: object, spatial_hint: str) -> None:
        """Slot ejecutado en el hilo principal de Qt para pintar el halo."""
        self.overlay.set_target_bbox(bbox, spatial_hint=spatial_hint)

    def _handle_clear_highlight(self) -> None:
        """Slot ejecutado en el hilo principal de Qt para limpiar el halo."""
        self.overlay.clear_highlight()

    async def process_user_query(self, user_query: str) -> None:
        """Ejecuta un ciclo de consulta, pinta el halo y muestra apoyo textual."""
        logger.info(f"Procesando consulta: '{user_query}'")
        resp = await self.coordinator.handle_user_request(user_query)

        # Si hay coordenadas fiables (Nivel A), emitir señal para dibujar halo
        if resp.visual_highlight:
            self.signals.show_highlight.emit(
                resp.visual_highlight,
                resp.spatial_description or "",
            )
        else:
            self.signals.clear_highlight.emit()

        # Nivel B/C: emitir señal para mostrar banner de texto grande si aplica
        if resp.spoken_text:
            self.signals.show_hint.emit(resp.spoken_text, 8000)

    def stop(self) -> None:
        """Detiene de forma limpia todos los componentes y bucles."""
        if not self._running:
            return
        logger.info("Deteniendo componentes de AsistenteApp...")
        self._running = False
        if hasattr(self, "wake_detector"):
            self.wake_detector.stop()
        if hasattr(self, "tray"):
            self.tray.hide()
        if hasattr(self, "overlay"):
            self.overlay.close()
        if hasattr(self, "fallback_banner"):
            self.fallback_banner.close()

    async def listen_loop(self) -> None:
        """
        Bucle continuo en segundo plano:
        1. Permanece en espera escuchando localmente por el Wake Word ("Sofia" / "hey asistente").
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
            if not self._running:
                break
            if not wake_detected or not self.wake_detector.is_listening():
                continue

            # 2. Indicar que el asistente está escuchando activamente (vía señal thread-safe)
            logger.info("✨ ¡Wake word detectado! Escuchando orden del usuario...")
            self.signals.show_hint.emit("🎤 Te escucho, dime qué necesitas...", 3000)
            await self.tts.speak("Sí, te escucho.")
            await asyncio.sleep(0.3)

            # 3. Grabar la intervención del usuario con tolerancia a pausas (1.8s)
            audio_bytes = await self.recorder.record_phrase_async()
            if not self._running:
                break
            if not audio_bytes:
                logger.info("No se capturó audio tras la activación.")
                self.signals.show_hint.emit(
                    f"ℹ️ No alcancé a escucharte. Vuelve a decir '{self.settings.wake_word}'.",
                    3000,
                )
                continue

            # 4. Transcribir orden a texto
            text = await self.stt.transcribe(audio_bytes)
            if not self._running:
                break
            if not text or len(text.strip()) < 2:
                logger.info("Transcripción vacía o inaudible.")
                continue

            logger.info(f"🗣️ Pregunta del usuario recibida: '{text}'")

            # 5. Procesar consulta en la sesión continua de chat
            await self.process_user_query(text)
