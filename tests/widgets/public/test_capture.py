"""Tests for `widget.capture()` (#427).

A capture reads pixels from the display, so what these can assert is limited on
purpose. Whether the saved image shows *this* application depends on what else
the machine has on screen, which no assertion can control — that question is
settled by `development/verify_427_capture.py`, which toggles the theme between
two captures and proves the pixels track this window. An earlier version of that
probe passed every geometry check while capturing a browser, which is exactly
why nothing here pretends to verify content.

What is asserted instead are the invariants that hold regardless of what is on
screen: the rectangle captured, the format chosen, the errors raised, and the
always-on-top setting left as it was found.
"""
from __future__ import annotations

import sys
import tkinter

import pytest
from PIL import Image, UnidentifiedImageError

import bootstack as bs
from bootstack._core import capture as _capture
from bootstack.errors import BootstackError

# `isolated` keeps these out of the shared-root leg, where accumulated tests
# push the widgets clean off the display and every grab asks for a region no
# monitor covers. See the note beside this module in `tests/run_gui.py`.
pytestmark = [pytest.mark.gui, pytest.mark.isolated]


def _monitors():
    """The display layout, or a skip when this machine cannot report one.

    Deliberately imported here rather than read off the capture module, so that
    running these against unfixed source fails on the BEHAVIOR under test and
    not on a missing attribute.
    """
    try:
        from screeninfo import get_monitors

        found = get_monitors()
    except Exception as exc:  # noqa: BLE001 - headless boxes raise several types
        pytest.skip(f"no display layout available: {exc}")
    if not found:
        pytest.skip("no monitors reported")
    return found


def test_capture_writes_the_file_and_returns_its_path(shown_app, tmp_path):
    label = bs.Label("capture me")
    shown_app.tk.update_idletasks()

    target = tmp_path / "shot.png"
    written = label.capture(target, settle=0)

    assert written == target
    assert written.is_file() and written.stat().st_size > 0


def test_capture_matches_the_widget_rectangle(shown_app, tmp_path):
    """The grab is the widget's own rect, not the window's."""
    label = bs.Label("measure me")
    shown_app.tk.update_idletasks()
    expected = (label.tk.winfo_width(), label.tk.winfo_height())

    with Image.open(label.capture(tmp_path / "rect.png", settle=0)) as img:
        assert img.size == expected


def test_inset_trims_every_edge(shown_app, tmp_path):
    label = bs.Label("trim me")
    shown_app.tk.update_idletasks()
    full = (label.tk.winfo_width(), label.tk.winfo_height())

    with Image.open(label.capture(tmp_path / "inset.png", inset=2, settle=0)) as img:
        assert img.size == (full[0] - 4, full[1] - 4)


def test_extension_selects_the_format(shown_app, tmp_path):
    """`.png`, `.jpg` and `.pdf` are the formats #425 asked for."""
    label = bs.Label("format me")
    shown_app.tk.update_idletasks()

    for suffix, expected in ((".png", "PNG"), (".jpg", "JPEG")):
        written = label.capture(tmp_path / f"shot{suffix}", settle=0)
        with Image.open(written) as img:
            assert img.format == expected

    # Pillow writes PDF but cannot read it back, so check the magic bytes.
    pdf = label.capture(tmp_path / "shot.pdf", settle=0)
    assert pdf.read_bytes()[:4] == b"%PDF"


def test_missing_parent_folders_are_created(shown_app, tmp_path):
    label = bs.Label("nested")
    shown_app.tk.update_idletasks()

    written = label.capture(tmp_path / "a" / "b" / "shot.png", settle=0)
    assert written.is_file()


def test_unknown_extension_raises_a_bootstack_error(shown_app, tmp_path):
    label = bs.Label("bad format")
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="extension selects the format"):
        label.capture(tmp_path / "shot.wat", settle=0)


def test_detached_widget_cannot_be_captured(shown_app, tmp_path):
    """The guard that stops a capture from silently grabbing whatever is behind."""
    label = bs.Label("gone")
    shown_app.tk.update_idletasks()
    label.detach()
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="not visible on screen"):
        label.capture(tmp_path / "detached.png", settle=0)


def test_inset_larger_than_the_widget_raises(shown_app, tmp_path):
    label = bs.Label("tiny")
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="trims away the whole capture"):
        label.capture(tmp_path / "over.png", inset=9999, settle=0)


def test_capture_restores_a_window_that_was_not_topmost(shown_app, tmp_path):
    """Capturing raises the window; it must put the setting back afterward."""
    root = shown_app.tk
    root.attributes("-topmost", False)
    root.update_idletasks()

    bs.Label("restore me").capture(tmp_path / "restore.png", settle=0)

    assert not root.attributes("-topmost")


def test_capture_leaves_a_deliberately_topmost_window_pinned(shown_app, tmp_path):
    """An application that pinned its window must not be un-pinned by a capture.

    This is the control for the test above: the same code path, opposite
    starting state, so a fix that simply forced the flag off would fail here.
    """
    root = shown_app.tk
    root.attributes("-topmost", True)
    root.update_idletasks()
    try:
        bs.Label("still pinned").capture(tmp_path / "pinned.png", settle=0)
        assert root.attributes("-topmost")
    finally:
        root.attributes("-topmost", False)


def test_negative_inset_raises(shown_app, tmp_path):
    """An inset trims. It must not be usable to photograph the neighbors."""
    label = bs.Label("no growing")
    shown_app.tk.update_idletasks()

    with pytest.raises(BootstackError, match="is negative"):
        label.capture(tmp_path / "grown.png", inset=-8, settle=0)


def test_widget_closed_while_settling_raises_a_bootstack_error(
    shown_app, tmp_path
):
    """Settling turns the event loop, so a queued handler can close the target.

    Without the guard the next line reads geometry from a dead widget and a raw
    toolkit error escapes a method documented to raise `BootstackError`. The
    control is every other test in this file: the same call without a pending
    destroy captures normally.
    """
    label = bs.Label("closing")
    shown_app.tk.update_idletasks()
    shown_app.tk.after(1, label.tk.destroy)

    with pytest.raises(BootstackError, match="closed while the capture"):
        label.capture(tmp_path / "gone.png", settle=0.1)


def test_a_no_alpha_format_converts_a_mode_the_grabbers_never_produce(tmp_path):
    """`save()` gates on the target format, not on one source mode.

    Reached through the internal function on purpose. The Windows and macOS
    grabbers only ever return RGB or RGBA, so this is unreachable from the
    public method on either box — it is the Linux fallback, which opens
    whatever the desktop screenshot tool wrote, that can produce a palette
    image.
    """
    palette = Image.new("P", (4, 4))

    with Image.open(_capture.save(palette, tmp_path / "flat.jpg")) as img:
        assert img.mode == "RGB"

    # Control: PNG stores a palette perfectly well, so nothing is converted.
    with Image.open(_capture.save(palette, tmp_path / "kept.png")) as img:
        assert img.mode == "P"


def test_a_region_outside_the_grab_raises_instead_of_padding_black():
    """A screenshot tool that missed the monitor must not yield a black picture.

    Cropping past the edge of an image pads the result with black and raises
    nothing, so the failure would reach the user as a plausible-looking
    all-black file with nothing to debug.
    """
    desktop = Image.new("RGB", (1920, 1080), "white")

    with pytest.raises(BootstackError, match="does not cover the area"):
        _capture._crop_desktop(desktop, (1930, 10, 2200, 300))

    # Control: a region the grab does cover crops normally.
    assert _capture._crop_desktop(desktop, (10, 10, 110, 60)).size == (100, 50)


def test_a_widget_scrolled_out_of_view_cannot_be_captured(shown_app, tmp_path):
    """Mapped is not the same as in view.

    A widget scrolled out of a viewport stays mapped and keeps reporting the
    position it would occupy if the window were tall enough to show it, so the
    grab reads whatever else is on screen there and saves it without
    complaining. Measured before the guard: a row reporting y=273 for a window
    spanning 390 to 630 captured successfully and produced a 1-color image,
    against 217 colors for the same row in view.
    """
    rows = []
    with bs.ScrollView(scroll_direction="vertical", height=120) as view:
        for i in range(30):
            with bs.Card(padding=6) as row:
                bs.Label(f"row {i}")
            rows.append(row)
    shown_app.tk.update_idletasks()
    shown_app.tk.update()

    first = rows[0]
    # Control: in view, the very same widget captures normally. Without this a
    # broken ScrollView would make the assertion below pass for free.
    assert first.capture(tmp_path / "in-view.png", settle=0).is_file()

    view.yview_moveto(0.5)
    shown_app.tk.update_idletasks()
    shown_app.tk.update()

    window_top = shown_app.tk.winfo_rooty()
    row_bottom = first.tk.winfo_rooty() + first.tk.winfo_height()
    # Preconditions, so this cannot pass for the wrong reason: the row really
    # did leave the window, and the toolkit really does still call it mapped —
    # if it did not, the older visibility guard would be the one raising.
    if row_bottom > window_top:
        pytest.skip("the viewport did not scroll the row out of the window")
    assert first.tk.winfo_ismapped()

    with pytest.raises(BootstackError, match="scrolled out of view"):
        first.capture(tmp_path / "scrolled-away.png", settle=0)


def test_a_destroyed_root_is_reported_gone_rather_than_raising(shown_app):
    """`winfo_exists()` answers for a dead child but RAISES for a dead root.

    Measured: a destroyed child returns 0, while a destroyed root raises
    `TclError: application has been destroyed` — there is no interpreter left
    to ask. Both mean "nothing to photograph", so both must answer False, or a
    raw toolkit error escapes a method documented to raise `BootstackError`.
    This is the App-level arm of the guard already fixed for child widgets.

    Asserted through the helper rather than through `capture()`: reaching it
    for real means destroying the root mid-settle, which would take the rest of
    this module's tests with it. So this guards against regression rather than
    reproducing the defect — unfixed source can only fail it for the
    uninteresting reason that the helper does not exist yet.
    """
    class DeadRoot:
        def winfo_exists(self):
            raise tkinter.TclError("application has been destroyed")

    assert _capture.still_exists(DeadRoot()) is False

    # Controls, through the real toolkit: alive, then destroyed.
    live = bs.Label("alive")
    shown_app.tk.update_idletasks()
    assert _capture.still_exists(live.tk) is True
    live.tk.destroy()
    assert _capture.still_exists(live.tk) is False


def test_a_region_on_no_display_names_the_real_cause(monkeypatch):
    """An off-display region must not be reported as a missing backend.

    Pillow reports a region no monitor covers as `UnidentifiedImageError`,
    which IS an `OSError` — the same exception raised by a Pillow built without
    XCB. Reading the first as the second sends a macOS user off to install
    Linux screenshot tools on a machine whose own backend works perfectly.

    The failure is forced rather than provoked with a real off-screen grab:
    Windows crops a whole-desktop grab and returns black instead of raising, so
    a test that leaned on the genuine failure would assert a macOS-only answer.
    """
    def refuse(*args, **kwargs):
        raise UnidentifiedImageError("cannot identify image file")

    monkeypatch.setattr(_capture.ImageGrab, "grab", refuse)
    # The real `sys`, not the capture module's reference to it — unfixed source
    # does not import `sys` at all, and patching through it would turn this
    # into an attribute error instead of the behavioral failure it should be.
    monkeypatch.setattr(sys, "platform", "darwin")

    monitors = _monitors()
    below_everything = max(m.y + m.height for m in monitors) + 5_000
    off = (10, below_everything, 110, below_everything + 100)

    with pytest.raises(BootstackError, match="not on any display") as nowhere:
        _capture.grab(off)
    assert "grim" not in str(nowhere.value)

    # Control: the identical forced failure over a region that IS on a display.
    # A different cause earns a different message — and neither one may send a
    # Mac user to install Linux tooling.
    first = monitors[0]
    on = (first.x + 10, first.y + 10, first.x + 60, first.y + 40)

    with pytest.raises(BootstackError, match="capture failed") as covered:
        _capture.grab(on)
    assert "grim" not in str(covered.value)


def test_a_window_hanging_off_the_edge_still_counts_as_on_screen():
    """The guard must refuse only what no monitor touches at all.

    A window dragged half off the bottom of the screen captures perfectly well
    — measured on macOS, which clamps such a window and grabs it in full — so
    treating partial overlap as off-display would reject a working capture.

    This one guards against a future over-rejection rather than reproducing the
    original defect: it exercises a helper that did not exist before the fix, so
    unfixed source can only fail it for the uninteresting reason.
    """
    monitors = _monitors()
    first = monitors[0]

    fully_on = (first.x + 10, first.y + 10, first.x + 60, first.y + 40)
    assert _capture._covered_by_a_display(fully_on) is True

    half_off = (first.x + 10, first.y + first.height - 20,
                first.x + 60, first.y + first.height + 200)
    assert _capture._covered_by_a_display(half_off) is True

    below_everything = max(m.y + m.height for m in monitors) + 5_000
    nowhere = (first.x + 10, below_everything, first.x + 60, below_everything + 100)
    assert _capture._covered_by_a_display(nowhere) is False
