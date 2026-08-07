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
import tempfile
import time
import tkinter
from pathlib import Path

from PIL import Image, ImageGrab

from bootstack.errors import BootstackError

# Formats that store plain color and nothing else. A capture bound for one of
# these is converted first, because saving an image that carries transparency
# — or a color palette — as JPEG fails outright.
_NO_ALPHA_FORMATS = {".jpg", ".jpeg", ".pdf", ".bmp"}

# Image modes those formats accept as they are.
_PLAIN_COLOR_MODES = ("RGB", "L")

# Tried in order, first one installed wins.
_SUBPROCESS_BACKENDS = (
    ("grim", ["grim", "{out}"]),                              # wlroots, Sway
    ("gnome-screenshot", ["gnome-screenshot", "-f", "{out}"]),
    ("spectacle", ["spectacle", "-b", "-n", "-o", "{out}"]),  # KDE
    ("import", ["import", "-window", "root", "{out}"]),       # ImageMagick
)


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

    Flushes the framework's own drawing, then yields for `seconds` so the
    desktop can repaint the area behind any window that has just closed — a
    save dialog, most commonly. The event loop keeps running throughout, so
    the interface does not freeze while this waits.

    Args:
        tk_widget: Any widget; its root window drives the event loop.
        seconds: How long to yield for. Zero flushes without waiting.
    """
    root = tk_widget._root()
    root.update_idletasks()
    root.update()
    deadline = time.monotonic() + max(seconds, 0.0)
    while time.monotonic() < deadline:
        time.sleep(0.01)
        root.update()


def capture_region(bbox: tuple[int, int, int, int], path) -> Path:
    """Grab one screen region and write it to `path`, returning the path."""
    return save(grab(bbox), path)


def grab(bbox: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Grab a screen region, or the whole primary display when `bbox` is None."""
    try:
        # `all_screens` widens the grab to the whole virtual desktop. Without
        # it, a region on a monitor left of or above the primary one is cropped
        # out of a primary-only grab and comes back silently BLACK — no
        # exception raised and nothing to debug. Pillow honors the flag on
        # Windows and ignores it elsewhere.
        return ImageGrab.grab(bbox=bbox, all_screens=bbox is not None)
    except (OSError, NotImplementedError):
        # Wayland, or a Pillow built without XCB.
        return _grab_via_subprocess(bbox)


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

    The screenshot tools photograph the desktop and return an image measured
    from their own origin, while the region is measured across the whole
    virtual desktop. Those agree on an ordinary single-monitor session and can
    disagree otherwise — most often when the window sits on a monitor the tool
    did not photograph. Cropping past the edge of an image pads the result with
    black rather than failing, so the caller would get a plausible-looking
    all-black picture and no way to tell why. Raising is the better answer.
    """
    left, top, right, bottom = bbox
    if left < 0 or top < 0 or right > image.width or bottom > image.height:
        raise BootstackError(
            f"The screen capture tool returned a {image.width}x{image.height} "
            f"picture, which does not cover the area being captured — "
            f"({left}, {top}) to ({right}, {bottom}). This usually means the "
            f"window is on a monitor the tool did not photograph; moving it to "
            f"the main display is the reliable workaround."
        )
    return image.crop(bbox)
