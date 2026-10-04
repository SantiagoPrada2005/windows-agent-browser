import ctypes
import logging
import platform
import subprocess
import sys
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ActiveWindowDetector(ABC):
    """
    Puerto abstracto para detectar el título de la ventana en primer plano del sistema operativo.
    """

    @abstractmethod
    def get_active_window_title(self) -> str:
        """Devuelve el título de la ventana activa actual."""
        pass


class WindowsActiveWindowDetector(ActiveWindowDetector):
    """Implementación nativa para Windows utilizando las funciones de la Win32 API vía ctypes."""

    def get_active_window_title(self) -> str:
        try:
            user32 = ctypes.windll.user32  # type: ignore[attr-defined]
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return "Escritorio de Windows"

            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return "Ventana sin título"

            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value.strip()
            return title if title else "Ventana sin título"
        except Exception as e:
            logger.debug(f"Error obteniendo ventana activa en Windows: {e}")
            return "Escritorio de Windows"


class FallbackActiveWindowDetector(ActiveWindowDetector):
    """Implementación de respaldo para macOS / Linux y entornos de desarrollo/testing."""

    def __init__(self, default_title: str = "Escritorio / Desconocido"):
        self.default_title = default_title

    def get_active_window_title(self) -> str:
        if platform.system() == "Darwin":
            try:
                # Intento ligero vía AppleScript en macOS sin dependencias externas
                cmd = (
                    'osascript -e \'tell application "System Events" to get name of first '
                    "application process whose frontmost is true'"
                )
                output = subprocess.check_output(
                    cmd, shell=True, stderr=subprocess.DEVNULL, timeout=0.3
                )
                app_name = output.decode("utf-8").strip()
                if app_name:
                    return f"{app_name} (macOS)"
            except Exception:
                pass
        return self.default_title


def get_default_window_detector() -> ActiveWindowDetector:
    """Factoría que retorna el detector adecuado según la plataforma actual."""
    if sys.platform == "win32":
        return WindowsActiveWindowDetector()
    return FallbackActiveWindowDetector()
