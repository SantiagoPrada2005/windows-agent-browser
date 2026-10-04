import pytest
from pydantic import ValidationError

from asistente_guiador.core.models import (
    BoundingBox,
    IntentResult,
    IntentType,
    VisualElementResult,
)


def test_bounding_box_pixel_conversion():
    bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
    px, py, pw, ph = bbox.to_pixel_coords(1920, 1080)

    assert px == 192
    assert py == 216
    assert pw == 576
    assert ph == 432


def test_bounding_box_out_of_bounds_validation():
    with pytest.raises(ValidationError):
        BoundingBox(x=1.5, y=0.0, width=0.1, height=0.1)


def test_intent_result_defaults():
    res = IntentResult(
        intent=IntentType.LOCATE_ELEMENT,
        target="Guardar",
        requires_visual_context=True,
    )
    assert res.intent == IntentType.LOCATE_ELEMENT
    assert res.target == "Guardar"
    assert res.requires_visual_context is True
    assert res.confidence == 1.0


def test_visual_element_result_structure():
    bbox = BoundingBox(x=0.05, y=0.05, width=0.05, height=0.05)
    vis = VisualElementResult(
        found=True,
        application="Microsoft Word",
        target="Guardar",
        confidence=0.95,
        bbox=bbox,
        spatial_description="Arriba a la izquierda, junto a la barra de acceso rápido",
        reason="Icono de disquete presente",
    )
    assert vis.found is True
    assert vis.bbox.x == 0.05
