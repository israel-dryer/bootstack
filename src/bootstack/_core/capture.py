"""Screen-region capture backing the public `widget.capture()`.

A capture reads pixels from the display, so the region has to be visible:
the widget must be on screen, and anything drawn over it is captured along
with it. There is no offscreen rendering path — the toolkit does not offer
one — which is why the public method requires a visible widget.

Capture uses Pillow's `ImageGrab`, falling back to a desktop screenshot tool
on Linux sessions where `ImageGrab` is unavailable (Wayland, or a Pillow
built without XCB support).
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import tkinter
from pathlib import Path

from PIL import Image, ImageGrab

from bootstack.errors import BootstackError

try:
    from screeninfo import get_monitors
    HAS_SCREENINFO = True
except ImportError:
    HAS_SCREENINFO = False

# Platforms whose capture backend ships with the operating system. There is
# nothing to install and nothing to fall back to, so a failure here is a real
# failure rather than a missing-backend one.
_BUILTIN_BACKEND_PLATFORMS = ("win32", "darwin")

# How long to pause between event-loop turns while settling. Short enough to
# stay responsive to the repaint we are waiting for, long enough not to spin.
_SETTLE_TICK = 0.01

# Formats that store plain color and nothing else. A capture bound for one of
# these is converted first, because saving an image that carries transparency
# — or a color palette — as JPEG fails outright.
_NO_ALPHA_FORMATS = {".jpg", ".jpeg", ".pdf", ".bmp"}

# Image modes those formats accept as they are.
_PLAIN_COLOR_MODES = ("RGB", "L")

# Tried in order, first one installed wins.
_SUBPROCESS_BACKENDS = (
    ("grim", ["grim", "{out}"]),                                    # wlroots, Sway
    ("gnome-screenshot", ["gnome-screenshot", "-f", "{out}"]),
    # `-f` asks for the full screen. Without it spectacle repeats whatever
    # capture mode it was last used with, which is remembered in its own
    # config — so the same call photographs the desktop on one machine and a
    # single window on the next.
    ("spectacle", ["spectacle", "-b", "-n", "-f", "-o", "{out}"]),  # KDE
    ("import", ["import", "-window", "root", "{out}"]),             # ImageMagick
)

# Platforms where cutting the region has to stay `ImageGrab`'s job, because it
# needs detail this module does not have. Windows crops against the origin its
# own grab reports, which cannot be reconstructed from a rectangle alone; macOS
# asks `screencapture` for the region and rescales the answer, which is what
# keeps the result aligned on a Retina display. Cutting the region here would
# discard both.
#
# This says which code owns the crop, not that the crop is checked — neither of
# those is. Windows pads a region reaching past the grabbed desktop with black,
# and macOS stretches a region the system clamped. Extending the bounds check to
# them is a separate change, and one no box available here can verify.
#
# Everywhere else — Linux — `ImageGrab` grabs the whole desktop and crops it
# with no check that it covers the region, padding the difference with black
# and raising nothing. That is the failure `_crop_desktop` refuses, so there
# the region is cut here rather than by the library.
_LIBRARY_REGION_PLATFORMS = ("win32", "darwin")
_LIBRARY_HANDLES_REGION = sys.platform in _LIBRARY_REGION_PLATFORMS


def widget_region(tk_widget, inset: int = 0) -> tuple[int, int, int, int]:
    """Return a widget's on-screen rectangle as `(left, top, right, bottom)`.

    Coordinates span the whole virtual desktop, so a widget on a monitor
    placed to the left of, or above, the primary one has a negative origin.

    Args:
        tk_widget: The toolkit widget to measure.
        inset: Pixels to trim from every edge. Zero or more.
    """
    if inset < 0:
        raise BootstackError(
            f"inset={inset} is negative. An inset trims pixels from every "
            f"edge, so it cannot reach past the widget onto its neighbors."
        )
    x, y = tk_widget.winfo_rootx(), tk_widget.winfo_rooty()
    width, height = tk_widget.winfo_width(), tk_widget.winfo_height()
    left, top = x + inset, y + inset
    right, bottom = x + width - inset, y + height - inset
    if right <= left or bottom <= top:
        raise BootstackError(
            f"inset={inset} trims away the whole capture — the widget is only "
            f"{width}x{height} pixels."
        )
    return (left, top, right, bottom)


def still_exists(tk_widget) -> bool:
    """Whether a widget is still alive, without leaking a toolkit error.

    `winfo_exists()` reports 0 for a destroyed child but RAISES for a destroyed
    root — the toolkit has no interpreter left to ask by then. Both mean the
    same thing to a caller, so both answer False here.
    """
    try:
        return bool(tk_widget.winfo_exists())
    except tkinter.TclError:
        return False


def clipped_out_of_view(tk_widget) -> bool:
    """Whether a widget's rectangle has left its own window entirely.

    A widget scrolled out of a viewport stays MAPPED — the toolkit reports
    `winfo_ismapped()` and `winfo_viewable()` as 1 for a row that is nowhere
    near the visible area — while `winfo_rooty()` keeps reporting where the row
    would be if the window were tall enough to show it. Measured: a row in a
    scrolled list reported y=273 for a window spanning 390 to 630.

    Capturing that rectangle photographs whatever else is on screen there and
    saves it without complaint, which is the one outcome this module exists to
    prevent. Only a rectangle that has left the window completely is refused;
    a row half out of view still captures, matching the rule that a capture
    shows what the screen shows.
    """
    top = tk_widget.winfo_toplevel()
    if tk_widget is top:
        return False

    left, top_y = tk_widget.winfo_rootx(), tk_widget.winfo_rooty()
    right = left + tk_widget.winfo_width()
    bottom = top_y + tk_widget.winfo_height()

    win_left, win_top = top.winfo_rootx(), top.winfo_rooty()
    win_right = win_left + top.winfo_width()
    win_bottom = win_top + top.winfo_height()

    return not (
        left < win_right and right > win_left
        and top_y < win_bottom and bottom > win_top
    )


@contextlib.contextmanager
def raised(tk_widget):
    """Hold a widget's window at the front for the duration of a capture.

    A capture reads whatever is on the display, so a window sitting over the
    target is captured instead of it — silently, and with a plausible-looking
    image to show for it. Raising the window first is what makes the result
    mean what the caller asked for.

    The previous always-on-top setting is restored on the way out, and left
    alone entirely if it was already set, so a window the application
    deliberately pinned on top does not get un-pinned by taking a picture.
    """
    top = tk_widget.winfo_toplevel()
    try:
        top.lift()
    except tkinter.TclError:
        pass

    # None means "left alone" — either the setting could not be read, or the
    # window manager does not support it. Some Linux window managers do not,
    # and a capture must not fail just because it cannot pin a window.
    was_topmost = None
    try:
        was_topmost = bool(top.attributes("-topmost"))
        if not was_topmost:
            top.attributes("-topmost", True)
    except tkinter.TclError:
        was_topmost = None

    try:
        yield
    finally:
        # Restore only what this function actually changed.
        if was_topmost is False:
            try:
                top.attributes("-topmost", False)
            except tkinter.TclError:
                pass


def settle(tk_widget, seconds: float) -> None:
    """Let pending redraws finish before the pixels are read.

    Waits `seconds` while the event loop turns, so the desktop can repaint
    the area behind any window that has just closed — a save dialog, most
    commonly.

    The wait has to dispatch events. Flushing our own drawing is not enough:
    the area a closing window uncovers is repainted by the desktop, and on
    macOS that repaint does not happen at all unless the loop is turning. A
    capture taken without it photographs the dialog that was just dismissed
    rather than the widget underneath.

    Dispatching brings its own problem, which is why the window is held busy
    for the duration. Turning the loop runs everything queued, including a
    second click on the button that started the capture: that click would
    re-enter the caller's handler, opening a second save dialog on top of the
    first and starting an overlapping capture, none of which the person
    clicking asked for. `tk busy` routes that click to a blocking window
    instead.

    ⚠ THE HOLD IS BEST-EFFORT, AND ON macOS IT DOES NOTHING. Aqua reports the
    hold as successful and never maps the window it created: `tk busy status`
    returns 1 while the busy window sits at `winfo_ismapped() == 0`, and Tk's
    own hit test at the button's position still resolves to the button. So a
    real click re-enters the handler there — confirmed by hand, since a
    synthesized click cannot test this. Measured on Tk 8.6.17 in plain
    tkinter, so it is the toolkit rather than anything above it. X11 and Win32
    map the window and are expected to honor it;
    `development/probe_429_busy_during_settle.py` reports which a given box
    does.

    The wait dispatches either way. A correct picture is worth more than a
    stray click: without dispatching, the capture reads pixels that are simply
    wrong, and that is the failure this function exists to prevent.

    Args:
        tk_widget: Any widget; its root window is the one flushed.
        seconds: How long to wait for. Zero flushes without waiting.
    """
    root = tk_widget._root()
    root.update_idletasks()
    with _input_blocked(tk_widget):
        deadline = time.perf_counter() + max(seconds, 0.0)
        while time.perf_counter() < deadline:
            root.update()
            # Yield the processor rather than spinning on update() alone.
            time.sleep(_SETTLE_TICK)
        # Once more after the wait, so anything the pause allowed to arrive
        # is drawn before the pixels are read.
        root.update()
    root.update_idletasks()


@contextlib.contextmanager
def _input_blocked(tk_widget):
    """Route input away from a window while the event loop is being turned.

    Yields either way: a window that cannot be held busy is still captured,
    just without the protection from a stray click.

    ⚠ Yielding `True` means the hold was ACCEPTED, not that input is actually
    blocked — macOS accepts it and does not map the busy window. See `settle`.

    ⚠ The target may already be DEAD by the time this runs — settling flushes
    pending drawing first, and idle work queued before the capture can destroy
    it. Asking a destroyed widget for its toplevel raises a raw `TclError`,
    which would escape a method documented to raise `BootstackError` and
    pre-empt the guard that reports the closure properly. So the lookup is
    guarded too, not just the `tk busy` calls.
    """
    top = None
    held = False
    try:
        top = tk_widget.winfo_toplevel()
        top.tk.call("tk", "busy", "hold", top._w)
        held = True
    except tkinter.TclError:
        held = False
    try:
        yield held
    finally:
        if held and top is not None:
            try:
                top.tk.call("tk", "busy", "forget", top._w)
            except tkinter.TclError:
                pass


def capture_region(bbox: tuple[int, int, int, int], path) -> Path:
    """Grab one screen region and write it to `path`, returning the path."""
    return save(grab(bbox), path)


def grab(bbox: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Grab a screen region, or the whole primary display when `bbox` is None."""
    try:
        if _LIBRARY_HANDLES_REGION:
            # `all_screens` widens the grab to the whole virtual desktop.
            # Without it, a region on a monitor left of or above the primary
            # one is cropped out of a primary-only grab and comes back
            # silently BLACK — no exception raised and nothing to debug.
            return ImageGrab.grab(bbox=bbox, all_screens=bbox is not None)
        # Grab the whole desktop and cut the region out below, under the
        # bounds check. This platform grabs everything and crops either way,
        # so what changes is where the crop happens, not how much is read.
        image = ImageGrab.grab()
    except (OSError, NotImplementedError) as exc:
        # Diagnosis happens only AFTER a failed grab, never before one, so
        # nothing here can reject a capture that would have worked.
        #
        # The catch is deliberately wide because the failures it has to cover
        # are: no ImageGrab on this build at all, and a grab that ran and came
        # back with nothing usable. Those need opposite answers, and the
        # exception type cannot tell them apart — Pillow reports a region no
        # display covers as `UnidentifiedImageError`, which IS an `OSError`.
        if bbox is not None and _covered_by_a_display(bbox) is False:
            raise BootstackError(
                f"The area being captured — ({bbox[0]}, {bbox[1]}) to "
                f"({bbox[2]}, {bbox[3]}) — is not on any display, so there are "
                f"no pixels to read. A window moved off the edge of the screen, "
                f"or a widget scrolled out of view, is the usual cause."
            ) from exc

        if sys.platform in _BUILTIN_BACKEND_PLATFORMS:
            # Falling through to the subprocess chain here would end in advice
            # to install Linux screenshot tools on a machine that already has a
            # working backend — wrong on its face and no help in fixing this.
            raise BootstackError(
                f"The screen capture failed — {exc}. The window may have been "
                f"hidden or moved while the picture was being taken."
            ) from exc

        # Wayland, or a Pillow built without XCB.
        return _grab_via_subprocess(bbox)
    # Outside the `except` on purpose: a region the grab missed is a capture
    # failure to report, not a reason to try another backend.
    return _crop_desktop(image, bbox) if bbox else image


def _covered_by_a_display(bbox: tuple[int, int, int, int]) -> bool | None:
    """Whether any monitor covers part of `bbox`.

    Returns None when the question cannot be answered — no `screeninfo`, or it
    could not read the display layout — so a caller can tell "definitely not on
    a display" apart from "could not tell", and only act on the former.

    Partial overlap counts as covered. A window hanging off the bottom edge of
    the screen captures perfectly well; only a region no monitor touches at all
    has nothing to read.
    """
    if not HAS_SCREENINFO:
        return None

    left, top, right, bottom = bbox
    try:
        monitors = get_monitors()
    except Exception:  # noqa: BLE001 - a diagnostic must not raise its own error
        return None
    if not monitors:
        return None

    return any(
        left < m.x + m.width and right > m.x
        and top < m.y + m.height and bottom > m.y
        for m in monitors
    )


def save(image: Image.Image, path) -> Path:
    """Write an image to `path`, taking the format from its extension."""
    path = Path(path)
    # Decided by the target format rather than one source mode: a desktop
    # screenshot tool can hand back a palette or grayscale-with-alpha image,
    # and those fail on the same formats RGBA does.
    if (
        path.suffix.lower() in _NO_ALPHA_FORMATS
        and image.mode not in _PLAIN_COLOR_MODES
    ):
        image = image.convert("RGB")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
    except (OSError, ValueError, KeyError) as exc:
        raise BootstackError(
            f"Could not save the capture to '{path}' — {exc}. The file "
            f"extension selects the format; '.png', '.jpg', and '.pdf' are "
            f"the usual choices."
        ) from exc
    return path


def _grab_via_subprocess(
    bbox: tuple[int, int, int, int] | None = None,
) -> Image.Image:
    """Capture through a desktop screenshot tool, for Linux without ImageGrab."""
    for name, argv in _SUBPROCESS_BACKENDS:
        if not shutil.which(name):
            continue
        # A unique name per call — a fixed one collides when two captures
        # overlap, and the loser silently reads the other's pixels.
        handle, tmp_name = tempfile.mkstemp(
            prefix="bootstack-capture-", suffix=".png"
        )
        os.close(handle)
        tmp = Path(tmp_name)
        try:
            subprocess.run(
                [arg.format(out=tmp) for arg in argv],
                check=True,
                capture_output=True,
                timeout=30,
            )
            with Image.open(tmp) as opened:
                opened.load()
                image = opened.copy()
        except (subprocess.SubprocessError, OSError):
            continue
        finally:
            tmp.unlink(missing_ok=True)
        return _crop_desktop(image, bbox) if bbox else image

    raise BootstackError(
        "No screen capture backend is available. Install a Pillow build with "
        "XCB support, or one of: grim, gnome-screenshot, spectacle, import."
    )


def _crop_desktop(
    image: Image.Image, bbox: tuple[int, int, int, int]
) -> Image.Image:
    """Cut a region out of a whole-desktop grab, refusing a region it misses.

    A whole-desktop grab returns an image measured from whatever its source
    treats as the origin, while the region is measured across the whole virtual
    desktop. Those agree on an ordinary single-monitor session and can disagree
    otherwise — most often when the window sits on a monitor the grab did not
    cover. Cropping past the edge of an image pads the result with black rather
    than failing, so the caller would get a plausible-looking all-black picture
    and no way to tell why. Raising is the better answer.
    """
    left, top, right, bottom = bbox
    if left < 0 or top < 0 or right > image.width or bottom > image.height:
        raise BootstackError(
            f"The screen capture returned a {image.width}x{image.height} "
            f"picture, which does not cover the area being captured — "
            f"({left}, {top}) to ({right}, {bottom}). Either the window is "
            f"hanging off the edge of the screen, or it is on a display the "
            f"capture did not reach. Moving it fully onto the main display "
            f"resolves both."
        )
    return image.crop(bbox)
