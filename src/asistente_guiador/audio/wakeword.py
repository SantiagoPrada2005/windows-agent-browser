import asyncio
import io
import logging
import wave

import numpy as np

try:
    import sounddevice as sd
except (ImportError, OSError):
    sd = None

from asistente_guiador.core.interfaces import STTProvider

logger = logging.getLogger(__name__)


class WakeWordAudioListener:
    """
    Detector continuo de Wake Word ("hey asistente"):
    - Escucha audio localmente en ventanas continuas de ~2.0 segundos.
    - Sólo cuando el audio supera el umbral de energía de voz, se transcribe.
    - Comprueba si el texto contiene la palabra de activación configurada.
    - Únicamente tras confirmar el Wake Word, dispara la activación del asistente.
    - No transmite audio si está pausado o en silencio absoluto.
    """

    def __init__(
        self,
        stt_provider: STTProvider,
        wake_word: str = "hey asistente",
        sample_rate: int = 16000,
        energy_threshold: float = 0.02,
        window_seconds: float = 2.0,
    ):
        self.stt = stt_provider
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.window_samples = int(sample_rate * window_seconds)
        self._is_listening = True

    def pause(self) -> None:
        """Pausa la detección desde la bandeja."""
        self._is_listening = False
        logger.info("Detector de Wake Word: PAUSADO")

    def resume(self) -> None:
        """Reanuda la detección."""
        self._is_listening = True
        logger.info("Detector de Wake Word: REANUDADO")

    def is_listening(self) -> bool:
        return self._is_listening

    def _record_audio_window(self) -> bytes | None:
        """Captura una ventana de audio local y comprueba si hay energía de habla."""
        if sd is None or not self._is_listening:
            return None

        try:
            # sd.rec devuelve directamente el array numpy (no una tupla)
            audio_data = sd.rec(
                frames=self.window_samples,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocking=True,
            )
            # Calcular energía RMS
            energy = float(np.sqrt(np.mean(audio_data**2)))
            if energy < self.energy_threshold:
                return None  # Silencio ambiente, no gastar llamadas STT

            # Convertir a WAV
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())

            return wav_buffer.getvalue()
        except Exception as e:
            logger.warning(f"Error capturando ventana de audio: {e}")
            return None

    async def wait_for_wake_word(self) -> bool:
        """
        Bucle no bloqueante que evalúa si el usuario pronunció el Wake Word.
        Devuelve True únicamente tras confirmar la palabra clave.
        """
        while self._is_listening:
            wav_bytes = await asyncio.to_thread(self._record_audio_window)
            if not wav_bytes:
                await asyncio.sleep(0.1)
                continue

            # Transcribir fragmento para verificar palabra clave
            text = await self.stt.transcribe(wav_bytes)
            if not text:
                continue

            clean = text.lower().strip()
            logger.debug(f"Detector WakeWord escuchó: '{clean}'")

            # Comprobar variantes de activación: 'hey asistente', 'asistente', 'oye asistente'
            target_words = [self.wake_word, "asistente", "oye asistente", "hola asistente"]
            if any(w in clean for w in target_words):
                logger.info(f"✨ ¡WAKE WORD DETECTADO!: '{clean}'")
                return True

        return False
