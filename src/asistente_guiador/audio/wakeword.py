import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WakeWordDetector(ABC):
    """Interfaz para detectores de palabra de activación (openWakeWord / emulador)."""

    @abstractmethod
    async def wait_for_wake_word(self) -> bool:
        """Espera de forma no bloqueante hasta que se detecta la palabra clave."""
        pass


class SimpleWakeWordDetector(WakeWordDetector):
    """
    Detector de Wake Word local.
    Soporta simulación y base para openWakeWord sin transmitir audio continuo (RF-01).
    """

    def __init__(self, wake_word: str = "hey asistente"):
        self.wake_word = wake_word.lower()
        self._is_listening = True

    def pause(self) -> None:
        """Pausa la detección desde la bandeja del sistema (RF-12)."""
        self._is_listening = False

    def resume(self) -> None:
        """Reanuda la escucha activa."""
        self._is_listening = True

    async def wait_for_wake_word(self) -> bool:
        """En entorno controlado o desarrollo simula activación bajo demanda."""
        if not self._is_listening:
            await asyncio.sleep(0.5)
            return False
        return True
