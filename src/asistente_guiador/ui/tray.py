import logging

from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

logger = logging.getLogger(__name__)


def create_tray_icon_pixmap(listening: bool = True) -> QPixmap:
    """Genera un icono circular dinámico (Verde=Escuchando, Naranja=Pausado)."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))  # Fondo transparente

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    color = QColor(46, 204, 113) if listening else QColor(230, 126, 34)
    painter.setBrush(color)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawEllipse(4, 4, 24, 24)
    painter.end()

    return pixmap


class SystemTrayManager(QSystemTrayIcon):
    """
    Controlador de la bandeja del sistema (System Tray) según PRD RF-12:
    - Permite pausar y reanudar la escucha en cualquier momento.
    - Proporciona acceso rápido a probar audio, limpiar overlay y salir.
    """

    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.is_listening = True

        self.setIcon(QIcon(create_tray_icon_pixmap(listening=True)))
        self.setToolTip("Asistente Guiador de Ofimática (Activo)")

        self._create_menu()
        self.setVisible(True)

    def _create_menu(self) -> None:
        menu = QMenu()

        # Acción de Estado / Pausa
        self.toggle_action = QAction("Pausar Escucha", self)
        self.toggle_action.triggered.connect(self.toggle_listening)
        menu.addAction(self.toggle_action)

        menu.addSeparator()

        # Limpiar overlay en pantalla
        clear_action = QAction("Limpiar Resaltado", self)
        clear_action.triggered.connect(self.clear_overlay)
        menu.addAction(clear_action)

        menu.addSeparator()

        # Salir de la aplicación
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def toggle_listening(self) -> None:
        """Pausa o reanuda la escucha activa."""
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.toggle_action.setText("Pausar Escucha")
            self.setIcon(QIcon(create_tray_icon_pixmap(listening=True)))
            self.setToolTip("Asistente Guiador de Ofimática (Activo)")
            self.app_controller.wake_detector.resume()
            self.showMessage(
                "Asistente Reanudado",
                "El micrófono está activo para recibir instrucciones.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            self.toggle_action.setText("Reanudar Escucha")
            self.setIcon(QIcon(create_tray_icon_pixmap(listening=False)))
            self.setToolTip("Asistente Guiador de Ofimática (Pausado)")
            self.app_controller.wake_detector.pause()
            self.showMessage(
                "Asistente Pausado",
                "El micrófono no escuchará hasta que lo reanudes.",
                QSystemTrayIcon.MessageIcon.Warning,
                2000,
            )

    def clear_overlay(self) -> None:
        """Limpia el halo actual."""
        if hasattr(self.app_controller, "overlay"):
            self.app_controller.overlay.clear_highlight()
