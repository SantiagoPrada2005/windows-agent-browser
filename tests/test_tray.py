from unittest.mock import MagicMock

from asistente_guiador.ui.tray import SystemTrayManager, create_tray_icon_pixmap


def test_create_tray_icon_pixmap():
    pix_active = create_tray_icon_pixmap(listening=True)
    assert not pix_active.isNull()
    assert pix_active.width() == 32

    pix_paused = create_tray_icon_pixmap(listening=False)
    assert not pix_paused.isNull()


def test_system_tray_toggle(qapp):
    mock_app = MagicMock()
    tray = SystemTrayManager(app_controller=mock_app)

    assert tray.is_listening is True

    # Simular clic en Pausar
    tray.toggle_listening()
    assert tray.is_listening is False
    mock_app.wake_detector.pause.assert_called_once()

    # Simular clic en Reanudar
    tray.toggle_listening()
    assert tray.is_listening is True
    mock_app.wake_detector.resume.assert_called_once()


def test_system_tray_clear_overlay(qapp):
    mock_app = MagicMock()
    tray = SystemTrayManager(app_controller=mock_app)
    tray.clear_overlay()
    mock_app.overlay.clear_highlight.assert_called_once()
