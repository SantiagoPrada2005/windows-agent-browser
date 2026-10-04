import cv2
import numpy as np
from PIL import Image


class ScreenChangeDetector:
    """
    Detector local de cambios visuales entre frames para evitar llamadas de API remotas.
    Utiliza diferencia absoluta en escala de grises y redimensionado para cálculo rápido.
    """

    def __init__(
        self,
        threshold_percentage: float = 0.03,
        check_size: tuple[int, int] = (640, 360),
    ):
        """
        :param threshold_percentage: Fracción de píxeles modificados para considerar un cambio.
        :param check_size: Resolución reducida para comparar frames rápidamente en CPU.
        """
        self.threshold_percentage = threshold_percentage
        self.check_size = check_size
        self._last_processed_frame: np.ndarray | None = None

    def _prepare_frame(self, image: Image.Image) -> np.ndarray:
        """Convierte una imagen PIL a un array OpenCV en escala de grises y tamaño reducido."""
        img_np = np.array(image.convert("RGB"))
        resized = cv2.resize(img_np, self.check_size, interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

    def compute_change_ratio(self, current_image: Image.Image) -> float:
        """
        Calcula el porcentaje de píxeles modificados respecto al frame anterior [0.0 - 1.0].
        Devuelve 1.0 si es el primer frame analizado.
        """
        current_frame = self._prepare_frame(current_image)
        if self._last_processed_frame is None:
            return 1.0

        diff = cv2.absdiff(self._last_processed_frame, current_frame)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        non_zero_count = np.count_nonzero(thresh)
        total_pixels = self.check_size[0] * self.check_size[1]
        return float(non_zero_count / total_pixels)

    def has_significant_change(self, current_image: Image.Image) -> bool:
        """
        Compara la imagen actual con la anterior registrada.
        Devuelve True si el cambio supera el umbral o si es el primer frame.
        """
        current_frame = self._prepare_frame(current_image)

        if self._last_processed_frame is None:
            self._last_processed_frame = current_frame
            return True

        change_ratio = self.compute_change_ratio(current_image)

        if change_ratio >= self.threshold_percentage:
            self._last_processed_frame = current_frame
            return True

        return False

    def reset(self) -> None:
        """Reinicia el estado del detector de cambios."""
        self._last_processed_frame = None
