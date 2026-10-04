import mss
from PIL import Image

from asistente_guiador.core.interfaces import ScreenCapturer


class MSSScreenCapturer(ScreenCapturer):
    """Capturador rápido de pantalla en memoria utilizando la librería mss."""

    def __init__(self, monitor_index: int = 1):
        self.monitor_index = monitor_index

    def capture_active_screen(self) -> Image.Image:
        with mss.mss() as sct:
            monitors = sct.monitors
            target_monitor = (
                monitors[self.monitor_index] if len(monitors) > self.monitor_index else monitors[0]
            )
            sct_img = sct.grab(target_monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
