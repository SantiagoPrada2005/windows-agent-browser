import logging
import sys

from PyQt6.QtWidgets import QApplication

from asistente_guiador.app import AsistenteApp
from asistente_guiador.config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("asistente_guiador")


def main() -> None:
    """Punto de entrada principal para la aplicación de escritorio."""
    settings = Settings()
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}...")

    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    # Mantener referencia viva en memoria
    _ = AsistenteApp(qapp=qapp)
    logger.info("Aplicación iniciada. Icono disponible en la bandeja del sistema.")

    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
