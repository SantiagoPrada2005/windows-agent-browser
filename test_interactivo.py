import asyncio
import logging
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from asistente_guiador.app import AsistenteApp
from asistente_guiador.config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("test_interactivo")


class InteractiveTester:
    """Ejecutor de pruebas interactivas en vivo sobre la pantalla actual."""

    def __init__(self, app: AsistenteApp):
        self.app = app

    async def run_scenario(self, user_query: str) -> None:
        logger.info("\n" + "=" * 60)
        logger.info(f'👉 INICIANDO CONSULTA: "{user_query}"')
        logger.info("Tomando captura de tu pantalla real y analizando...")
        logger.info("=" * 60)

        # 1. Mostrar estado de pantalla continuo actual
        screen_state = self.app.coordinator.session.global_screen_state
        logger.info(f"🖥️ Ventana activa detectada: '{screen_state.active_window_title}'")
        logger.info(f"📋 Resumen semántico en memoria: '{screen_state.screen_summary}'")

        # 2. Procesar consulta con captura real, LLM y modelo de visión
        resp = await self.app.coordinator.handle_user_request(user_query)

        # 3. Renderizar Halo sobre las coordenadas reales en la pantalla
        if resp.visual_highlight:
            logger.info(f"✨ ¡Elemento localizado! BoundingBox: {resp.visual_highlight}")
            logger.info(f"📍 Descripción espacial: {resp.spatial_description}")
            self.app.overlay.set_target_bbox(
                resp.visual_highlight,
                spatial_hint=resp.spatial_description,
            )
        else:
            logger.info("ℹ️ No se requirió o no se encontró resaltado visual específico.")
            self.app.overlay.clear_highlight()

        # 4. Mostrar banner flotante de accesibilidad
        if resp.spoken_text:
            logger.info(f'🔊 Respuesta verbal generada: "{resp.spoken_text}"')
            self.app.fallback_banner.show_hint(resp.spoken_text, duration_ms=10000)

        # 5. Síntesis de voz
        logger.info("Reproduciendo audio...")
        await self.app.tts.speak(resp.spoken_text)


def main():
    settings = Settings()
    print("=" * 65)
    print(f"  PRUEBA INTERACTIVA EN VIVO - {settings.app_name}")
    print("=" * 65)
    print("Este test capturará tu pantalla actual para localizar lo que pidas.")
    print("Ejemplos comunes:")
    print(" 1. ¿Dónde guardo este documento?")
    print(" 2. ¿Dónde está el menú Archivo?")
    print(" 3. ¿Dónde está la opción de buscar o el menú de búsqueda?")
    print(" 4. ¿Cómo pongo la letra en negrita?")
    print(" 5. ¿Qué tengo en la pantalla?")
    print(" 6. ¿Dónde le doy?")
    print("-" * 65)

    examples = {
        "1": "¿Dónde guardo este documento?",
        "2": "¿Dónde está el menú Archivo?",
        "3": "¿Dónde está la opción de buscar o el menú de búsqueda?",
        "4": "¿Cómo pongo la letra en negrita?",
        "5": "¿Qué tengo en la pantalla?",
        "6": "¿Dónde le doy?",
    }

    default_query = "¿Dónde está la opción de buscar o el menú de búsqueda?"
    try:
        prompt_msg = f"Ingresa consulta o número [1-6, o Enter para '{default_query}']: "
        user_input = input(prompt_msg).strip()
        if user_input in examples:
            query = examples[user_input]
        elif user_input:
            query = user_input
        else:
            query = default_query
    except EOFError:
        query = default_query

    qapp = QApplication(sys.argv)
    app = AsistenteApp(qapp=qapp)
    tester = InteractiveTester(app)

    # Disparar la consulta en el event loop después de que la ventana PyQt cargue
    def start_query():
        asyncio.run(tester.run_scenario(query))
        print("\n✅ Prueba ejecutada.")
        print("El halo y el banner permanecerán en tu pantalla durante 10 segundos.")
        QTimer.singleShot(10000, qapp.quit)

    QTimer.singleShot(500, start_query)
    qapp.exec()


if __name__ == "__main__":
    main()
