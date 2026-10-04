import asyncio
import logging
import signal
import sys
import threading

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from asistente_guiador.app import AsistenteApp
from asistente_guiador.config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("asistente_guiador")


def start_background_listener(app_instance: AsistenteApp) -> None:
    """Ejecuta el bucle continuo de escucha asíncrono en un hilo secundario."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(app_instance.listen_loop())
    except Exception as e:
        logger.error(f"Error en bucle de escucha en segundo plano: {e}")
    finally:
        loop.close()


def main() -> None:
    """Punto de entrada principal para la aplicación de escritorio."""
    settings = Settings()
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}...")

    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    app_instance = AsistenteApp(qapp=qapp)
    qapp.aboutToQuit.connect(app_instance.stop)

    # Configurar salida limpia por Ctrl+C (SIGINT / SIGBREAK / SIGTERM)
    def handle_exit_signal(*_):
        logger.info("🛑 Señal de cierre recibida (Ctrl+C). Cerrando aplicación...")
        app_instance.stop()
        qapp.quit()

    signal.signal(signal.SIGINT, handle_exit_signal)
    try:
        signal.signal(signal.SIGTERM, handle_exit_signal)
    except (AttributeError, ValueError):
        pass

    if hasattr(signal, "SIGBREAK"):
        try:
            signal.signal(signal.SIGBREAK, handle_exit_signal)
        except (AttributeError, ValueError):
            pass

    # QTimer periódico para que el loop de Qt ceda control a Python y procese señales
    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(200)

    logger.info("Aplicación iniciada. Icono disponible en la bandeja del sistema.")
    logger.info(
        "ℹ️ Para finalizar: presiona Ctrl+C en esta terminal o 'Salir' en la bandeja."
    )

    # Lanzar hilo en segundo plano para escuchar el micrófono y el wake word continuamente
    listener_thread = threading.Thread(
        target=start_background_listener,
        args=(app_instance,),
        daemon=True,
    )
    listener_thread.start()

    exit_code = qapp.exec()
    app_instance.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
