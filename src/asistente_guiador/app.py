import asyncio
import logging

from PyQt6.QtWidgets import QApplication

from asistente_guiador.ai.providers.groq_provider import GroqLLMProvider
from asistente_guiador.ai.providers.vision_provider import OpenRouterVisionProvider
from asistente_guiador.audio.recorder import VoiceActivityRecorder
from asistente_guiador.audio.stt import GroqWhisperSTTProvider
from asistente_guiador.audio.tts import PiperTTSProvider
from asistente_guiador.audio.wakeword import EnergyWakeWordDetector
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
        self.wake_detector = EnergyWakeWordDetector()

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
        Bucle continuo en segundo plano (Wake Word + STT + Asistencia):
        1. Espera a que el usuario empiece a hablar.
        2. Graba la frase completa respetando pausas.
        3. Transcribe el audio con Groq Whisper.
        4. Si detecta la palabra clave o consulta directa, ejecuta la asistencia.
        """
        logger.info("🎤 Bucle de escucha continua activado. Esperando voz...")
        while self._running:
            if not self.wake_detector.is_listening():
                await asyncio.sleep(0.5)
                continue

            # 1. Esperar activación de voz
            speech_started = await self.wake_detector.wait_for_speech()
            if not speech_started or not self.wake_detector.is_listening():
                continue

            # 2. Grabar frase con tolerancia a silencios (1.8s)
            logger.info("Grabando pregunta del usuario...")
            audio_bytes = await self.recorder.record_phrase_async()
            if not audio_bytes:
                continue

            # 3. Transcribir a texto con Whisper
            logger.info("Transcribiendo orden...")
            text = await self.stt.transcribe(audio_bytes)
            if not text or len(text.strip()) < 3:
                continue

            logger.info(f"Transcripción recibida: '{text}'")

            # 4. Comprobar palabra clave o atender consulta directa
            clean_text = text.lower()
            wake_word = self.settings.wake_word.lower()

            if wake_word in clean_text:
                # Quitar wake word para dejar la orden limpia
                clean_query = clean_text.replace(wake_word, "").strip(" ,.¡!¿?")
                if not clean_query:
                    await self.tts.speak("Sí, te escucho. ¿Qué necesitas hacer?")
                    continue
                await self.process_user_query(clean_query)
            else:
                # Si la frase parece una orden ofimática directa
                await self.process_user_query(text)
