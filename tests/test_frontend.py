from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def test_drag_and_drop_uses_pointer_events() -> None:
    """Le placement par glissement prend en charge la souris et le tactile."""
    script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'addEventListener("pointerdown"' in script
    assert 'addEventListener("pointermove", movePointerDrag' in script
    assert 'addEventListener("pointerup", finishPointerDrag' in script
    assert "elementFromPoint(clientX, clientY)" in script


def test_draggable_controls_disable_native_touch_gestures() -> None:
    """Les pions réservent les gestes tactiles au glisser-déposer du jeu."""
    stylesheet = (STATIC_DIR / "style.css").read_text(encoding="utf-8")

    assert stylesheet.count("touch-action: none") >= 2
