from unittest.mock import MagicMock, patch

from asistente_guiador.vision.window_detector import (
    ActiveWindowDetector,
    FallbackActiveWindowDetector,
    WindowsActiveWindowDetector,
    get_default_window_detector,
)


def test_fallback_window_detector():
    detector = FallbackActiveWindowDetector(default_title="Bloc de Notas")
    with patch("platform.system", return_value="Linux"):
        assert detector.get_active_window_title() == "Bloc de Notas"


def test_windows_active_window_detector_handles_error():
    detector = WindowsActiveWindowDetector()
    # En macOS/Linux o si ctypes falla, debe retornar fallback seguro sin lanzar excepción
    title = detector.get_active_window_title()
    assert isinstance(title, str)
    assert len(title) > 0


def test_get_default_window_detector_factory():
    detector = get_default_window_detector()
    assert isinstance(detector, ActiveWindowDetector)
    title = detector.get_active_window_title()
    assert isinstance(title, str)


def test_windows_window_detector_mocked_success():
    detector = WindowsActiveWindowDetector()
    mock_user32 = MagicMock()
    mock_user32.GetForegroundWindow.return_value = 12345
    expected_text = "Documento1 - Microsoft Word"
    mock_user32.GetWindowTextLengthW.return_value = len(expected_text)

    def fake_get_window_text(hwnd, buf, maxlen):
        buf.value = expected_text
        return len(expected_text)

    mock_user32.GetWindowTextW.side_effect = fake_get_window_text

    with patch("ctypes.windll", create=True) as mock_windll:
        mock_windll.user32 = mock_user32
        title = detector.get_active_window_title()
        assert title == "Documento1 - Microsoft Word"
