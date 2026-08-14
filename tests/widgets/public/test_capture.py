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
import time
import tkinter
import types

import pytest
from PIL import Image, UnidentifiedImageError

import bootstack as bs
from bootstack._core import capture as _capture
from bootstack.errors import BootstackError

# A color nothing in the theme uses, so any of it in a capture came from the
# test's own cover window rather than from the application.
_COVER_COLOR = "#ff00ff"

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


def _pin(root, timeout: float = 0.5) -> bool:
    """Pin a window on top, reporting whether the setting actually took.

    Always-on-top is a request to the window manager, not something the
    application decides. A session without a window manager — a headless test
    display, most often — leaves the setting unset and raises nothing, so both
    tests below would otherwise be measuring the window manager rather than the
    capture. Measured on a bare X server: setting it reads back 0, with no
    capture involved anywhere.

    A window manager that does honor the request answers asynchronously, and
    that answer arrives as a window event rather than an idle callback — so the
    read is polled rather than taken once. Reading too early reports "not
    supported" on the machines that support it perfectly well, which would skip
    both tests on exactly the boxes able to run them.
    """
    root.attributes("-topmost", True)
    deadline = time.monotonic() + timeout
    while True:
        root.update()
        if root.attributes("-topmost"):
            return True
        if time.monotonic() >= deadline:
            break
        time.sleep(0.01)
    # Put the request back where it was found. A refused request still leaves
    # one recorded, and the next caller reads that record rather than the
    # window manager — which made this very check report differently depending
    # on whether a previous test had already tried. Measured: the two tests
    # below both skipped when run alone, and the second one passed when run
    # after the first.
    root.attributes("-topmost", False)
    root.update_idletasks()
    return False


def _topmost_settles_to(root, expected: bool, timeout: float = 0.5) -> bool:
    """Poll `-topmost` until it reaches `expected`, and report what it ended at.

    The mirror of `_pin`'s poll, for the way back out. Always-on-top is a
    request the window manager answers asynchronously, and that is as true of
    clearing it as of setting it — so a single read taken right after a capture
    can see the state the window manager has not caught up to yet. Measured on
    X11: the restore lands in about a millisecond, but a read taken immediately
    still returns the old value, which failed this test on every Linux run while
    passing on Windows and macOS, where the attribute is answered synchronously.
    """
    deadline = time.monotonic() + timeout
    while True:
        root.update()
        if bool(root.attributes("-topmost")) == expected:
            return expected
        if time.monotonic() >= deadline:
            return bool(root.attributes("-topmost"))
        time.sleep(0.01)


def test_capture_restores_a_window_that_was_not_topmost(shown_app, tmp_path):
    """Capturing raises the window; it must put the setting back afterward."""
    root = shown_app.tk
    # Without this the assertion below is free: where the setting never takes,
    # "left off" cannot be told from "never went on".
    if not _pin(root):
        pytest.skip("this window manager does not honor always-on-top")
    # `update()`, not `update_idletasks()`: clearing the setting is answered by
    # the window manager the same way setting it is.
    root.attributes("-topmost", False)
    root.update()

    bs.Label("restore me").capture(tmp_path / "restore.png", settle=0)

    assert not _topmost_settles_to(root, False)


def test_capture_leaves_a_deliberately_topmost_window_pinned(shown_app, tmp_path):
    """An application that pinned its window must not be un-pinned by a capture.

    This is the control for the test above: the same code path, opposite
    starting state, so a fix that simply forced the flag off would fail here.
    """
    root = shown_app.tk
    if not _pin(root):
        pytest.skip("this window manager does not honor always-on-top")
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
    """Settling flushes pending drawing, so idle work can close the target.

    Without the guard the next line reads geometry from a dead widget and a raw
    toolkit error escapes a method documented to raise `BootstackError`. The
    control is every other test in this file: the same call without a pending
    destroy captures normally.

    ⚠ The destroy is queued as IDLE work, not on a timer. Settling stopped
    dispatching events for #429, so an `after(1, ...)` no longer runs during it
    and this test would pass without ever destroying anything — vacuous, and
    green either way. Idle callbacks are what `update_idletasks()` still runs,
    which is the path that remains open.
    """
    label = bs.Label("closing")
    shown_app.tk.update_idletasks()
    shown_app.tk.after_idle(label.tk.destroy)

    with pytest.raises(BootstackError, match="closed while the capture"):
        label.capture(tmp_path / "gone.png", settle=0.1)


def test_settling_repaints_the_area_a_closed_window_uncovered(
    shown_app, tmp_path
):
    """The capture must show the widget, not the dialog that just closed — #429.

    This is the whole point of settling. A save dialog sits over the target and
    the capture happens the moment it closes, so the desktop has to repaint the
    uncovered area before the pixels are read. On macOS that repaint does not
    happen at all unless the event loop is turning, and the resulting file is a
    photograph of the dismissed dialog — through the public method, following
    the pattern the docstring teaches.

    The cover is a distinctive color so the assertion is about CONTENT rather
    than geometry: any of it left in the frame means the stale pixels were
    captured. Measured before the fix, this arm caught 51400 of 60800 pixels.

    ⚠ Settling stopped dispatching for a first pass at #429 and this exact
    scenario is what that broke, so the assertion is deliberately not on the
    settle mechanism but on the picture it produces.

    ⚠ The window is SIZED, and both the window and the saved image are checked
    before the content assertion. The shared root collapses to 1x1 with no
    content of its own, and a one-pixel capture sampling one point away from
    the cover would report a clean picture no matter how broken settling was.
    """
    top = shown_app.tk.winfo_toplevel()
    # ⚠ Released in the finally below, and released rather than restored. The
    # root is SHARED, and any explicit geometry left on it — including the one
    # it had before — pins the window at that size, so later tests' widgets
    # land outside it and the scrolled-out-of-view guard refuses to capture
    # them. That surfaced as two failures in tests this one never touched.
    # An empty geometry hands sizing back to the content.
    try:
        top.geometry("320x200")
        shown_app.tk.update()

        # Precondition: the size request was actually serviced. Without this
        # the content assertion below can pass on a degenerate rectangle.
        assert top.winfo_width() >= 200 and top.winfo_height() >= 120, (
            f"the window is {top.winfo_width()}x{top.winfo_height()}, too "
            f"small for a capture that could show anything"
        )

        cover = tkinter.Toplevel(shown_app.tk)
        cover.overrideredirect(True)
        cover.configure(background=_COVER_COLOR)
        cover.geometry(
            f"{top.winfo_width()}x{top.winfo_height()}"
            f"+{top.winfo_rootx()}+{top.winfo_rooty()}"
        )
        cover.lift()
        cover.attributes("-topmost", True)
        shown_app.tk.update()
        # Closed the way a dialog closes: torn down, with no pumping after.
        cover.destroy()

        saved = shown_app.capture(tmp_path / "uncovered.png", settle=0.3)
    finally:
        top.wm_geometry("")
        shown_app.tk.update()

    with Image.open(saved) as img:
        width, height = img.size
        pixels = list(img.convert("RGB").getdata())

    # Second precondition, on the image rather than the window: a grab that
    # came back tiny cannot say anything about what is in the frame.
    assert width >= 200 and height >= 120, (
        f"the capture is {width}x{height}, too small to judge its content"
    )

    stale = sum(1 for r, g, b in pixels if r > 200 and g < 80 and b > 200)
    assert stale == 0, (
        f"{stale} of {len(pixels)} pixels still show the closed window, so the "
        f"capture photographed it instead of the application"
    )


def test_settling_holds_the_window_busy_while_it_dispatches(
    shown_app, tmp_path
):
    """Dispatching is what repaints, so input is blocked for the duration — #429.

    Turning the event loop runs everything queued, including a second click on
    the button that started the capture: that click would re-enter the caller's
    handler and stack a second save dialog. `tk busy` routes it to a blocking
    window instead.

    Observed from inside the settle window, using the very dispatching this
    guards: a timer scheduled to land mid-settle reads the busy state. The
    assertions after the call are its controls — the timer really did fire (so
    the reading is not of an empty list), and the hold is released on the way
    out (so it does not leak onto the application).

    ⚠ This asserts the hold is REQUESTED AND RELEASED, which is all that is
    portable. It does NOT assert that input is blocked, and `tk busy status`
    is not evidence that it is: macOS returns 1 for a busy window it never
    maps, so the hold is accepted and does nothing and a real click re-enters
    the handler. Confirmed by hand on Tk 8.6.17/aqua, and reproduced in plain
    tkinter, so it is the toolkit rather than anything above it.

    Whether a given platform honors the hold is arm 0 of
    `development/probe_429_busy_during_settle.py` — it checks the busy window
    is mapped and that Tk's hit test at a button resolves to it. That is
    deliberately not asserted here, because it is platform-dependent and would
    make this test fail on macOS for something it is not testing.

    ⚠ A synthesized click cannot stand in for the manual check either:
    `event_generate` aimed at a widget delivers straight to its bindings and
    never consults the busy window, so it re-enters whether the hold is real
    or not. The swallowing half is
    `development/demo_429_busy_during_settle.py`, by hand.
    """
    label = bs.Label("settling")
    shown_app.tk.update()
    top = label.tk.winfo_toplevel()

    def busy_status() -> str:
        return str(top.tk.call("tk", "busy", "status", top._w))

    assert busy_status() == "0", "the window was already busy before settling"

    seen: list[str] = []
    shown_app.tk.after(60, lambda: seen.append(busy_status()))

    label.capture(tmp_path / "shot.png", settle=0.3)

    assert seen == ["1"], (
        "the window was not held busy while settling dispatched events"
        if seen
        else "the timer never fired, so settling did not dispatch at all"
    )
    assert busy_status() == "0", "settling left the window busy"


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


def test_the_bounds_check_covers_the_library_path_not_only_the_fallback(
    monkeypatch,
):
    """`grab()` must not hand the region to a cropper that does not check it.

    Where the imaging library serves a region by grabbing the whole desktop
    first, it crops without checking that what it grabbed covers the region —
    it pads the difference with black and raises nothing. So the guard has to
    sit on that path too, not only on the subprocess fallback.

    Measured against the unfixed code with an undersized grab and a window
    outside it: a capture saved a 400x300 file of one color, all black, and
    raised nothing at all.
    """
    grabbed = Image.new("RGB", (800, 600), "white")
    monkeypatch.setattr(_capture, "_LIBRARY_HANDLES_REGION", False)
    monkeypatch.setattr(
        _capture, "ImageGrab", types.SimpleNamespace(grab=lambda *a, **k: grabbed)
    )

    with pytest.raises(BootstackError, match="does not cover the area"):
        _capture.grab((10, 10, 2000, 100))

    # Control: a region that grab does cover still comes back cropped.
    assert _capture.grab((10, 10, 110, 60)).size == (100, 50)


def test_the_region_stays_the_libraries_job_where_the_platform_needs_it(
    monkeypatch,
):
    """The opposite direction of the test above, which only forces it off.

    Windows crops against the origin its own grab reports, and macOS asks
    `screencapture` for the region and rescales the answer — the rescale being
    what keeps a Retina capture aligned. Cutting the region here instead would
    silently break both, on boxes this suite is usually not running on. So the
    hand-off is asserted rather than left implied: the library receives the
    rectangle, and nothing here crops or bounds-checks it.
    """
    grabbed = Image.new("RGB", (800, 600), "white")
    calls = []

    def record(*args, **kwargs):
        calls.append(kwargs)
        return grabbed

    monkeypatch.setattr(_capture, "_LIBRARY_HANDLES_REGION", True)
    monkeypatch.setattr(
        _capture, "ImageGrab", types.SimpleNamespace(grab=record)
    )

    # A region the grab does not cover: proof the crop was not taken over here,
    # since doing so would raise exactly as the test above requires.
    assert _capture.grab((10, 10, 2000, 100)) is grabbed
    assert calls == [{"bbox": (10, 10, 2000, 100), "all_screens": True}]


def test_only_windows_and_macos_leave_the_region_to_the_library():
    """Guard the platform list itself, which both tests above have to force.

    Each of them monkeypatches the flag, so dropping a platform from the list
    would leave the pair green while changing what every capture on that
    platform does. Restating the mapping is the cost of catching that.

    The list is asserted rather than the flag derived from it. Comparing the
    flag against `sys.platform` looks equivalent and is vacuous everywhere it
    is False: on Linux, deleting the exemption entirely left both sides False
    and the assertion green. Measured — that was this test's first version.
    """
    assert _capture._LIBRARY_REGION_PLATFORMS == ("win32", "darwin")
    assert _capture._LIBRARY_HANDLES_REGION == (
        sys.platform in _capture._LIBRARY_REGION_PLATFORMS
    )
