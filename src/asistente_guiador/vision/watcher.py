import asyncio
import logging

from PIL import Image

from asistente_guiador.core.interfaces import ScreenCapturer, VisionProvider
from asistente_guiador.core.session_state import SessionState
from asistente_guiador.vision.change_detector import ScreenChangeDetector
from asistente_guiador.vision.window_detector import (
    ActiveWindowDetector,
    get_default_window_detector,
)

logger = logging.getLogger(__name__)


class ScreenContextWatcher:
    """
    Observador continuo en segundo plano que mantiene el estado global de la pantalla de Windows.
    - Captura periódica en RAM con ScreenCapturer.
    - Detección de ventana activa del sistema operativo con ActiveWindowDetector.
    - Detección de cambios de imagen con ScreenChangeDetector.
    - Actualización debounced del resumen semántico global con VisionProvider ante cambios
      estructurales mayores.
    """

    def __init__(
        self,
        screen_capturer: ScreenCapturer,
        session_state: SessionState,
        vision_provider: VisionProvider | None = None,
        window_detector: ActiveWindowDetector | None = None,
        change_detector: ScreenChangeDetector | None = None,
        interval_seconds: float = 1.0,
        structural_threshold: float = 0.12,
        debounce_seconds: float = 1.0,
    ):
        self.capturer = screen_capturer
        self.session = session_state
        self.vision = vision_provider
        self.window_detector = window_detector or get_default_window_detector()
        self.change_detector = change_detector or ScreenChangeDetector()
        self.interval_seconds = interval_seconds
        self.structural_threshold = structural_threshold
        self.debounce_seconds = debounce_seconds

        self._running = False
        self._task: asyncio.Task | None = None
        self._last_window_title: str = ""
        self._debounce_task: asyncio.Task | None = None

    async def tick(self) -> bool:
        """
        Ejecuta un ciclo individual de inspección de pantalla.
        Devuelve True si se detectó algún cambio visual o de ventana.
        """
        try:
            current_image: Image.Image = self.capturer.capture_active_screen()
            current_window: str = self.window_detector.get_active_window_title()

            window_changed = bool(
                self._last_window_title and current_window != self._last_window_title
            )
            change_ratio = self.change_detector.compute_change_ratio(current_image)
            pixel_changed = self.change_detector.has_significant_change(current_image)

            structural_change = window_changed or (change_ratio >= self.structural_threshold)
            has_changed = pixel_changed or window_changed

            self._last_window_title = current_window

            # Actualizar frame y metadatos en SessionState
            self.session.update_screen_context(
                image=current_image,
                window_title=current_window,
                has_changed=has_changed,
            )

            # Si hubo cambio estructural y hay visión disponible, programar actualización semántica
            if structural_change and self.vision:
                self._schedule_semantic_update(current_image, current_window)

            return has_changed
        except Exception as e:
            logger.error(f"Error en ciclo de inspección de pantalla (tick): {e}")
            return False

    def _schedule_semantic_update(self, image: Image.Image, window_title: str) -> None:
        """Programa la actualización semántica debounced en segundo plano."""
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        async def _delayed_update():
            try:
                await asyncio.sleep(self.debounce_seconds)
                logger.info(
                    f"Actualizando resumen semántico global para ventana: '{window_title}'..."
                )
                summary = await self.vision.summarize_screen(image, active_window=window_title)
                self.session.update_screen_summary(summary)
                logger.info("Resumen semántico global actualizado exitosamente.")
            except asyncio.CancelledError:
                pass
            except Exception as ex:
                logger.warning(f"Error actualizando resumen semántico en segundo plano: {ex}")

        try:
            loop = asyncio.get_running_loop()
            self._debounce_task = loop.create_task(_delayed_update())
        except RuntimeError:
            pass

    async def _loop(self) -> None:
        logger.info(f"ScreenContextWatcher iniciado (intervalo={self.interval_seconds}s)")
        try:
            while self._running:
                await self.tick()
                await asyncio.sleep(self.interval_seconds)
        except asyncio.CancelledError:
            pass

    def start(self) -> asyncio.Task:
        """Inicia el bucle asíncrono en segundo plano."""
        if self._running and self._task:
            return self._task
        self._running = True
        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._loop())
        return self._task

    def stop(self) -> None:
        """Detiene de forma limpia el bucle y tareas de debounce."""
        self._running = False
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("ScreenContextWatcher detenido.")

    @property
    def is_running(self) -> bool:
        return self._running
