import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from asistente_guiador.core.models import BoundingBox
from asistente_guiador.overlay.fallback_hint import FloatingHintBanner
from asistente_guiador.overlay.overlay import TransparentOverlayWidget


@pytest.fixture(scope="session")
def qapp():
    """Crea una instancia de QApplication para pruebas sin GUI real."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["--platform", "offscreen"])
    return app


def test_overlay_widget_attributes(qapp):
    widget = TransparentOverlayWidget()
    # Verificar que no intercepta clicks del ratón (PRD RNF-07)
    assert widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) is True
    assert widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) is True


def test_overlay_bounding_box_assignment(qapp):
    widget = TransparentOverlayWidget()
    bbox = BoundingBox(x=0.1, y=0.1, width=0.2, height=0.1)

    widget.set_target_bbox(bbox, spatial_hint="Arriba a la izquierda")
    assert widget._highlight_rect is not None
    assert widget._spatial_hint == "Arriba a la izquierda"

    widget.clear_highlight()
    assert widget._highlight_rect is None


def test_fallback_hint_banner(qapp):
    banner = FloatingHintBanner()
    banner.show_hint("Presiona el botón Guardar en la barra superior.", duration_ms=2000)
    assert "Guardar" in banner.label.text()
