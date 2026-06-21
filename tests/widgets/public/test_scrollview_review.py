"""ScrollView review fixes (feat/scrollview-review).

The audit surfaced one real defect and one cleanup:

1. `add()` bound the content frame's `<Configure>` handler twice. The framework's
   `bind()` auto-adds, so the duplicate made `_on_frame_configure` (a recursive
   bindtag walk of the whole subtree + scrollregion/visibility recompute) run
   **twice on every resize**. Removed the duplicate.
2. A dead `import tkinter` in the public wrapper.

These also lock down behaviors that an audit pass wrongly flagged as bugs but are
in fact correct: a vertical wheel does nothing in `scroll_direction='horizontal'`,
and the canvas background tracks a runtime theme toggle.
"""
import pytest

import bootstack as bs
from bootstack.widgets._impl.composites.scrollview import ScrollView as _ISV
from bootstack.widgets._impl.primitives.frame import Frame as _Frame


# ----- the double-fire fix -----

def test_configure_handler_fires_once_per_resize(app):
    # bind() auto-adds, so add() must bind <Configure> exactly once; a duplicate
    # bind doubled the recursive subtree walk on every layout change.
    sv = _ISV(app._tk_root, height=150)
    sv.pack()
    calls = []
    sv._on_frame_configure = lambda e: calls.append(1)
    content = _Frame(sv.canvas)
    sv.add(content)
    app._tk_root.update_idletasks()
    calls.clear()
    content.event_generate("<Configure>", when="now")
    app._tk_root.update_idletasks()
    assert len(calls) == 1


# ----- construction across every mode / direction -----

@pytest.mark.parametrize("direction", ["vertical", "horizontal", "both"])
@pytest.mark.parametrize("visibility", ["always", "never", "hover", "scroll"])
def test_constructs_for_every_mode_and_direction(app, direction, visibility):
    sv = bs.ScrollView(
        scroll_direction=direction,
        scrollbar_visibility=visibility,
        height=80,
        width=120,
    )
    with sv:
        bs.Label("x")
    app._tk_root.update_idletasks()
    assert sv._internal._direction == direction


# ----- direction is honored on the wheel -----

def test_horizontal_mode_ignores_vertical_wheel(app):
    sv = bs.ScrollView(scroll_direction="horizontal", height=100, width=200)
    with sv:
        for i in range(30):
            bs.Label(f"row {i}")
    app._tk_root.update_idletasks()
    canvas = sv._internal.canvas
    before = canvas.yview()[0]

    class _WheelEvent:
        delta = -120
        num = 0

    sv._internal._on_mousewheel(_WheelEvent())
    app._tk_root.update_idletasks()
    assert canvas.yview()[0] == before  # vertical wheel is a no-op in horizontal mode


# ----- canvas background tracks the theme -----

def test_canvas_background_tracks_theme_toggle(shown_app):
    # The canvas theme-repaint is gated on winfo_viewable(), so the root must be
    # mapped — use the shown shared app.
    app = shown_app
    sv = bs.ScrollView(height=120)
    with sv:
        bs.Label("x")
    app._tk_root.update_idletasks()
    bs.set_theme("bootstrap-light")
    app._tk_root.update_idletasks()
    light_bg = sv._internal.canvas.cget("bg")
    bs.set_theme("bootstrap-dark")
    app._tk_root.update_idletasks()
    dark_bg = sv._internal.canvas.cget("bg")
    assert light_bg != dark_bg
