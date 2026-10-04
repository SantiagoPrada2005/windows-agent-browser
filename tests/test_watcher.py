import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from PIL import Image

from asistente_guiador.core.interfaces import ScreenCapturer, VisionProvider
from asistente_guiador.core.session_state import SessionState
from asistente_guiador.vision.watcher import ScreenContextWatcher
from asistente_guiador.vision.window_detector import ActiveWindowDetector


class DummyCapturer(ScreenCapturer):
    def __init__(self, color=(255, 255, 255)):
        self.color = color

    def capture_active_screen(self) -> Image.Image:
        return Image.new("RGB", (640, 360), color=self.color)


@pytest.mark.asyncio
async def test_watcher_tick_updates_session_state():
    session = SessionState()
    capturer = DummyCapturer(color=(100, 100, 100))
    window_detector = MagicMock(spec=ActiveWindowDetector)
    window_detector.get_active_window_title.return_value = "Documento1 - Microsoft Word"

    watcher = ScreenContextWatcher(
        screen_capturer=capturer,
        session_state=session,
        window_detector=window_detector,
        interval_seconds=0.1,
    )

    has_changed = await watcher.tick()

    assert has_changed is True
    assert session.global_screen_state.active_window_title == "Documento1 - Microsoft Word"
    assert session.last_screenshot is not None
    assert session.global_screen_state.has_structural_change is True


@pytest.mark.asyncio
async def test_watcher_structural_change_triggers_semantic_summary():
    session = SessionState()
    capturer = DummyCapturer(color=(200, 200, 200))
    window_detector = MagicMock(spec=ActiveWindowDetector)
    window_detector.get_active_window_title.return_value = "Guardar como"

    mock_vision = AsyncMock(spec=VisionProvider)
    mock_vision.summarize_screen.return_value = (
        "Cuadro de diálogo de guardado con botones Guardar y Cancelar."
    )

    watcher = ScreenContextWatcher(
        screen_capturer=capturer,
        session_state=session,
        vision_provider=mock_vision,
        window_detector=window_detector,
        interval_seconds=0.05,
        debounce_seconds=0.05,
    )

    await watcher.tick()
    # Esperar a que se ejecute la tarea debounced
    await asyncio.sleep(0.12)

    mock_vision.summarize_screen.assert_awaited_once_with(
        session.last_screenshot,
        active_window="Guardar como",
    )
    assert (
        session.global_screen_state.screen_summary
        == "Cuadro de diálogo de guardado con botones Guardar y Cancelar."
    )


@pytest.mark.asyncio
async def test_watcher_start_stop_lifecycle():
    session = SessionState()
    capturer = DummyCapturer()
    window_detector = MagicMock(spec=ActiveWindowDetector)
    window_detector.get_active_window_title.return_value = "Bloc de notas"

    watcher = ScreenContextWatcher(
        screen_capturer=capturer,
        session_state=session,
        window_detector=window_detector,
        interval_seconds=0.02,
    )

    task = watcher.start()
    assert watcher.is_running is True
    await asyncio.sleep(0.05)
    watcher.stop()
    await asyncio.sleep(0.01)
    assert watcher.is_running is False
    assert task.cancelled() or task.done()
