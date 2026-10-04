import asyncio
import logging

import numpy as np

try:
    import sounddevice as sd
except (ImportError, OSError):
    sd = None

logger = logging.getLogger(__name__)


class EnergyWakeWordDetector:
    """
    Detector de activación por voz / Wake Word para el bucle en segundo plano.
    Escucha de forma continua y ligera en el micrófono:
    1. Monitorea bloques de audio con sounddevice.
    2. Cuando detecta energía de voz por encima del umbral de ruido ambiente,
       activa la captura de la frase completa del usuario.
    3. Permite pausar/reanudar desde el System Tray.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        energy_threshold: float = 0.02,
        block_duration_ms: int = 200,
    ):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold
        self.block_size = int(sample_rate * (block_duration_ms / 1000.0))
        self._is_listening = True

    def pause(self) -> None:
        """Pausa la escucha desde la bandeja."""
        self._is_listening = False
        logger.info("Detector de activación: PAUSADO")

    def resume(self) -> None:
        """Reanuda la escucha."""
        self._is_listening = True
        logger.info("Detector de activación: REANUDADO")

    def is_listening(self) -> bool:
        return self._is_listening

    def wait_for_speech_sync(self) -> bool:
        """Bloquea hasta que detecta voz sobre el micrófono o se pausa."""
        if sd is None or not self._is_listening:
            return False

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32") as stream:
                while self._is_listening:
                    chunk, _ = stream.read(self.block_size)
                    energy = float(np.sqrt(np.mean(chunk**2)))
                    if energy > self.energy_threshold:
                        logger.info(f"Voz detectada: {energy:.3f} > {self.energy_threshold}")
                        return True
        except Exception as e:
            logger.warning(f"Error en stream de audio: {e}")
        return False

    async def wait_for_speech(self) -> bool:
        """Espera de forma no bloqueante a que el usuario empiece a hablar."""
        if not self._is_listening:
            await asyncio.sleep(0.5)
            return False
        return await asyncio.to_thread(self.wait_for_speech_sync)
