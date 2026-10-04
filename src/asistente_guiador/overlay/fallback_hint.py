from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class FloatingHintBanner(QWidget):
    """
    Ventana flotante de apoyo (Nivel B y C de degradación funcional del PRD - Sección 11).
    Se activa cuando la precisión de coordenadas no es segura o como refuerzo textual
    con tipografía grande y alto contraste para personas mayores.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._setup_ui()

        # Timer para auto-ocultar después de unos segundos
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)

        self.label = QLabel(self)
        self.label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            """
            QLabel {
                background-color: #1A1A24;
                color: #FFFFFF;
                border: 2px solid #FFD700;
                border-radius: 10px;
                padding: 12px 18px;
            }
            """
        )
        layout.addWidget(self.label)

    def show_hint(self, message: str, duration_ms: int = 8000) -> None:
        """Muestra el mensaje guiado en pantalla durante un tiempo predeterminado."""
        self.label.setText(f"💡 {message}")
        self.adjustSize()
        self.show()
        self._hide_timer.start(duration_ms)
