import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Instancia compartida de QApplication para tests offscreen con PyQt6."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["--platform", "offscreen"])
    return app
