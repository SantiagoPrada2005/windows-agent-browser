from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

from asistente_guiador.core.models import BoundingBox


class TransparentOverlayWidget(QWidget):
    """
    Ventana de overlay transparente (Always-on-top) para Windows/macOS.
    Características clave según PRD Sección 11 y RNF-07:
    - WA_TransparentForMouseEvents: NUNCA intercepta clics ni eventos de ratón.
    - WindowStaysOnTopHint + FramelessWindowHint: Flota sobre Word o Bloc de Notas.
    - Dibuja un halo brillante con bordes suaves alrededor de las coordenadas del botón.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._highlight_rect: QRect | None = None
        self._spatial_hint: str | None = None

        # Configuración de ventana transparente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def set_target_bbox(self, bbox: BoundingBox | None, spatial_hint: str | None = None) -> None:
        """Actualiza el halo según las coordenadas normalizadas [0.0 - 1.0]."""
        self._spatial_hint = spatial_hint
        if bbox is None:
            self._highlight_rect = None
            self.update()
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            return

        geo = screen.geometry()
        px, py, pw, ph = bbox.to_pixel_coords(geo.width(), geo.height())
        # Añadir un pequeño margen de padding visual (6px)
        padding = 6
        self._highlight_rect = QRect(
            max(0, px - padding),
            max(0, py - padding),
            pw + (padding * 2),
            ph + (padding * 2),
        )
        self.update()

    def clear_highlight(self) -> None:
        """Elimina el halo visual."""
        self._highlight_rect = None
        self._spatial_hint = None
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._highlight_rect:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Halo exterior difuso (Nivel A del PRD)
        outer_pen = QPen(QColor(255, 165, 0, 160), 6)  # Naranja accesible
        painter.setPen(outer_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self._highlight_rect, 10, 10)

        # 2. Borde interior sólido brillante
        inner_pen = QPen(QColor(255, 215, 0, 240), 2)  # Dorado brillante
        painter.setPen(inner_pen)
        painter.drawRoundedRect(self._highlight_rect, 8, 8)

        # 3. Pequeño indicador / flecha o etiqueta discreta si existe
        if self._spatial_hint:
            painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            painter.setPen(QColor(20, 20, 20, 230))
            painter.setBrush(QColor(255, 255, 220, 220))
            text_rect = QRect(
                self._highlight_rect.left(),
                max(10, self._highlight_rect.bottom() + 6),
                max(200, self._highlight_rect.width() + 40),
                26,
            )
            painter.drawRoundedRect(text_rect, 4, 4)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter,
                "👉 Mira aquí",
            )
