from PIL import Image

from asistente_guiador.vision.change_detector import ScreenChangeDetector


def test_change_detector_first_frame_always_changes():
    detector = ScreenChangeDetector()
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    assert detector.has_significant_change(img) is True


def test_change_detector_identical_frames_no_change():
    detector = ScreenChangeDetector()
    img1 = Image.new("RGB", (800, 600), color=(255, 255, 255))
    assert detector.has_significant_change(img1) is True

    # Segundo frame idéntico
    img2 = Image.new("RGB", (800, 600), color=(255, 255, 255))
    assert detector.has_significant_change(img2) is False


def test_change_detector_significant_modification():
    detector = ScreenChangeDetector(threshold_percentage=0.05)
    img_white = Image.new("RGB", (800, 600), color=(255, 255, 255))
    detector.has_significant_change(img_white)

    # Frame con cambio masivo de color
    img_black = Image.new("RGB", (800, 600), color=(0, 0, 0))
    assert detector.has_significant_change(img_black) is True
