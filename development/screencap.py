"""Cross-platform screen capture and OS printing helpers.

A standalone, dependency-light utility for capturing the screen, a window,
or a single widget, and for handing a file to the operating system's
printer. Written for discussion #425; not part of the public API.

Capture uses Pillow's `ImageGrab`, with a subprocess fallback for Linux
desktops where `ImageGrab` is unavailable (Wayland, or a Pillow built
without XCB). Printing shells out to the platform's native print path.

Multi-monitor is handled: coordinates are virtual-desktop coordinates, so
a monitor placed left of or above the primary one has negative origins.
Monitors are enumerated with `screeninfo`, the same library the framework's
own window-positioning code uses.

Requires: pillow, screeninfo

Run `screencap_demo.py` for a live example.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageGrab

try:
    from screeninfo import get_monitors
    HAS_SCREENINFO = True
except ImportError:  # mirrors the framework's own optional-import guard
    HAS_SCREENINFO = False

WINDOWS = sys.platform == "win32"
MACOS = sys.platform == "darwin"


class Monitor(NamedTuple):
    """One display, in virtual-desktop coordinates."""

    x: int
    y: int
    width: int
    height: int
    name: str
    is_primary: bool

    @property
    def bbox(self):
        """The monitor as a `(left, top, right, bottom)` capture region."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


def list_monitors():
    """Return every attached monitor, primary first.

    Coordinates are virtual-desktop coordinates: a monitor to the left of,
    or above, the primary one has a negative `x` or `y`.
    """
    if not HAS_SCREENINFO:
        return []
    try:
        found = get_monitors()
    except Exception:
        # screeninfo raises on some headless/exotic setups; treat as unknown.
        return []

    monitors = [
        Monitor(m.x, m.y, m.width, m.height,
                m.name or f"display-{i}", bool(getattr(m, "is_primary", False)))
        for i, m in enumerate(found)
    ]
    monitors.sort(key=lambda m: not m.is_primary)
    return monitors


def monitor_at(x, y):
    """Return the monitor containing a point, or `None` if it is off-screen."""
    for monitor in list_monitors():
        if monitor.x <= x < monitor.x + monitor.width and \
                monitor.y <= y < monitor.y + monitor.height:
            return monitor
    return None


def monitor_for_widget(widget):
    """Return the monitor a widget's center sits on, or `None`."""
    tk_widget = getattr(widget, "tk", widget)
    x = tk_widget.winfo_rootx() + tk_widget.winfo_width() // 2
    y = tk_widget.winfo_rooty() + tk_widget.winfo_height() // 2
    return monitor_at(x, y)


# --------------------------------------------------------------------------
# Capture
# --------------------------------------------------------------------------

def capture_screen(path=None, *, bbox=None, all_screens=None):
    """Capture the screen and return a Pillow image.

    Args:
        path: Optional file to save the capture to. The extension picks
            the format (`.png` is the safe default for UI captures).
        bbox: Optional `(left, top, right, bottom)` region in virtual-desktop
            coordinates, which may be negative on a multi-monitor setup.
            Captures the primary monitor when omitted.
        all_screens: Span every monitor. Defaults to `True` whenever `bbox`
            is given, because a region is addressed in virtual-desktop
            coordinates and those are only reachable when the whole desktop
            is in the grab. Windows only; ignored elsewhere.
    """
    if all_screens is None:
        # Without this, a bbox on a monitor left of or above the primary one
        # is cropped from a primary-only grab and comes back as a silently
        # BLACK image — no exception, no clue. Measured on a two-monitor
        # setup with the secondary at x=-2560.
        all_screens = bbox is not None

    try:
        image = ImageGrab.grab(bbox=bbox, all_screens=all_screens)
    except (OSError, NotImplementedError):
        # Linux without XCB, or a Wayland session.
        image = _grab_via_subprocess(bbox)

    if image.mode == "RGBA":
        image = image.convert("RGB")
    if path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
    return image


def capture_widget(widget, path=None, *, inset=0, delay=0.15):
    """Capture the screen region occupied by a widget or window.

    The capture is a screen grab of the widget's rectangle, so the widget
    must be visible and unobstructed. Pass an app, a window, or any widget.

    Args:
        widget: A bootstack widget, window, or app.
        path: Optional file to save the capture to.
        inset: Pixels to trim from each edge. Use `2` to drop the native
            window-border artifact when capturing a whole window.
        delay: Seconds to wait after raising the window, so the compositor
            has finished drawing before the pixels are read. This blocks
            briefly, which is fine from a button handler. To defer a capture
            without blocking, use `widget.schedule.delay(ms, fn)` and call
            `capture_screen` from the callback, as `screencap_demo.py` does.
    """
    # `.tk` is the documented escape hatch. It is used here because reading a
    # widget's screen rectangle, and forcing a repaint before the grab, have no
    # public equivalent — the toolkit owns both. Confined to this function.
    tk_widget = getattr(widget, "tk", widget)

    top = tk_widget.winfo_toplevel()
    top.lift()
    top.attributes("-topmost", True)
    top.update_idletasks()
    top.update()
    time.sleep(delay)

    x, y = tk_widget.winfo_rootx(), tk_widget.winfo_rooty()
    w, h = tk_widget.winfo_width(), tk_widget.winfo_height()
    bbox = (x + inset, y + inset, x + w - inset, y + h - inset)

    try:
        return capture_screen(path, bbox=bbox)
    finally:
        top.attributes("-topmost", False)


def capture_monitor(monitor=0, path=None):
    """Capture one whole monitor.

    Args:
        monitor: A `Monitor` from `list_monitors()`, or an index into it
            (`0` is the primary display).
        path: Optional file to save the capture to.
    """
    if not isinstance(monitor, Monitor):
        monitors = list_monitors()
        if not monitors:
            raise RuntimeError(
                "Could not enumerate monitors — is `screeninfo` installed?"
            )
        try:
            monitor = monitors[monitor]
        except IndexError:
            raise IndexError(
                f"No monitor at index {monitor}; {len(monitors)} attached."
            ) from None
    return capture_screen(path, bbox=monitor.bbox)


def _grab_via_subprocess(bbox=None):
    """Fall back to a desktop screenshot tool (Linux/Wayland)."""
    tools = [
        ("grim", ["grim", "{out}"]),                      # wlroots / Sway
        ("gnome-screenshot", ["gnome-screenshot", "-f", "{out}"]),
        ("spectacle", ["spectacle", "-b", "-n", "-o", "{out}"]),  # KDE
        ("import", ["import", "-window", "root", "{out}"]),       # ImageMagick
    ]
    for name, argv in tools:
        if not shutil.which(name):
            continue
        out = Path(tempfile.gettempdir()) / f"_capture_{os.getpid()}.png"
        try:
            subprocess.run(
                [a.format(out=out) for a in argv],
                check=True,
                capture_output=True,
                timeout=30,
            )
            image = Image.open(out)
            image.load()
            out.unlink(missing_ok=True)
            return image.crop(bbox) if bbox else image
        except (subprocess.SubprocessError, OSError):
            continue

    raise RuntimeError(
        "No screen capture backend available. Install a Pillow build with "
        "XCB support, or one of: grim, gnome-screenshot, spectacle, import."
    )


# --------------------------------------------------------------------------
# Printing
# --------------------------------------------------------------------------

def list_printers():
    """Return the names of installed printers."""
    if WINDOWS:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Printer | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, timeout=30,
        )
    else:
        if not shutil.which("lpstat"):
            return []
        result = subprocess.run(
            ["lpstat", "-e"], capture_output=True, text=True, timeout=30
        )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def print_file(path, *, printer=None, copies=1):
    """Send a file to a printer using the operating system's print path.

    On Windows this invokes the shell's registered `print` verb for the
    file type, which for images opens the Windows photo-printing wizard.
    On macOS and Linux it submits the file to CUPS via `lp`.

    Args:
        path: File to print.
        printer: Printer name. Uses the system default when omitted.
            Ignored on Windows, which routes through the shell verb.
        copies: Number of copies. Ignored on Windows.
    """
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    if WINDOWS:
        # `print` is a shell verb registered per file type. Images resolve to
        # the Photo Printing Wizard; other types depend on the installed
        # handler, and some (PDF, plain text) may have none at all. The call
        # is asynchronous and typically shows a dialog.
        try:
            os.startfile(str(path), "print")
        except OSError as exc:
            raise RuntimeError(
                f"No print handler is registered for '{path.suffix}' files."
            ) from exc
        return

    if not shutil.which("lp"):
        raise RuntimeError("Printing requires CUPS (`lp` was not found).")

    argv = ["lp"]
    if printer:
        argv += ["-d", printer]
    if copies > 1:
        argv += ["-n", str(copies)]
    argv.append(str(path))
    subprocess.run(argv, check=True, capture_output=True, timeout=60)


def print_image(image, *, printer=None, copies=1):
    """Print a Pillow image by writing it to a temporary file first."""
    tmp = Path(tempfile.gettempdir()) / f"_print_{os.getpid()}.png"
    image.save(tmp)
    print_file(tmp, printer=printer, copies=copies)