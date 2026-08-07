"""Cross-platform verification for `widget.capture()` (#427).

Run this on every platform before the feature ships. It is written to be run
on Windows, macOS, and Linux unchanged: arms that do not apply to the machine
report SKIP rather than failing, and arms whose behavior is platform-dependent
report what they measured instead of asserting a Windows answer everywhere.

The arm that matters most is `capture tracks a theme toggle`. Geometry checks
cannot tell this application apart from whatever window happens to occupy the
same rectangle — an earlier version of this probe passed every geometry check
while capturing a browser. Toggling the theme changes this window's pixels and
nothing else's, so two captures that differ is causal proof the grab is reading
this application.

That same arm is how a macOS box reports a missing Screen Recording permission:
without it the system hands back a picture of the desktop with no windows in it
and raises nothing, so the two captures come back identical.

Run: py -3.12 development/verify_427_capture.py     (Windows)
     python development/verify_427_capture.py       (macOS, Linux)
"""

import platform
import sys
import tkinter
from pathlib import Path

from PIL import Image, ImageChops, ImageGrab
from screeninfo import get_monitors

import bootstack as bs
from bootstack import errors as bs_errors

OUT = Path(__file__).parent / "screencap_out"
results = []


def check(name, condition, detail=""):
    results.append((name, "PASS" if condition else "FAIL", detail))


def skip(name, why):
    results.append((name, "SKIP", why))


def note(name, detail):
    results.append((name, "NOTE", detail))


def distinct_colors(source):
    img = source if isinstance(source, Image.Image) else Image.open(source)
    try:
        colors = img.convert("RGB").getcolors(maxcolors=1_000_000)
    finally:
        if img is not source:
            img.close()
    return len(colors) if colors else 999_999


def mean_difference(path_a, path_b):
    """Average per-pixel difference between two saved captures."""
    with Image.open(path_a) as a, Image.open(path_b) as b:
        first, second = a.convert("RGB"), b.convert("RGB")
        if first.size != second.size:
            return 255.0
        diff = ImageChops.difference(first, second).convert("L")
        pixels = first.size[0] * first.size[1]
        return sum(v * c for v, c in enumerate(diff.histogram())) / pixels


def banner():
    print()
    print(f"  platform : {sys.platform} ({platform.platform()})")
    print(f"  python   : {sys.version.split()[0]}")
    print(f"  tk       : {tkinter.TkVersion}")
    print(f"  pillow   : {getattr(Image, '__version__', 'unknown')}")
    for m in get_monitors():
        primary = getattr(m, "is_primary", None)
        print(f"  monitor  : {m.name} at ({m.x}, {m.y}) "
              f"{m.width}x{m.height} primary={primary}")
    # Which backend Pillow will use. A Linux session without XCB, or Wayland,
    # falls through to a desktop screenshot tool instead.
    try:
        ImageGrab.grab(bbox=(0, 0, 4, 4))
        print("  backend  : Pillow ImageGrab")
    except (OSError, NotImplementedError) as exc:
        print(f"  backend  : subprocess fallback (ImageGrab unavailable: {exc})")
    print()


def run_checks():
    # --- basics -------------------------------------------------------------
    png = app.capture(OUT / "verify-app.png", inset=2)
    check("returns the path it wrote", png == OUT / "verify-app.png")
    check("file exists and is non-empty", png.is_file() and png.stat().st_size > 0)

    with Image.open(png) as img:
        size = img.size
    expected = (app.tk.winfo_width() - 4, app.tk.winfo_height() - 4)
    check("size matches the widget rect minus inset", size == expected,
          f"got {size}, expected {expected}")

    colors = distinct_colors(png)
    check("NOT a blank image", colors > 1, f"{colors} distinct colors")

    # --- THE control: is this actually OUR window? --------------------------
    bs.toggle_theme()
    app.tk.update_idletasks()
    toggled = app.capture(OUT / "verify-app-toggled.png", inset=2)
    delta = mean_difference(png, toggled)
    tracks = delta > 10
    check("capture tracks a theme toggle (it IS our window)", tracks,
          f"mean pixel delta {delta:.1f} (identical would be 0.0)")
    if not tracks and sys.platform == "darwin":
        note("macOS hint",
             "identical captures usually mean Screen Recording permission is "
             "not granted to the terminal or interpreter running this")
    bs.toggle_theme()
    app.tk.update_idletasks()

    # --- a single widget ----------------------------------------------------
    widget_png = card.capture(OUT / "verify-widget.png")
    with Image.open(widget_png) as img:
        widget_size = img.size
    check("a single widget captures its own smaller rect",
          widget_size[0] < size[0] and widget_size[1] < size[1],
          f"widget {widget_size} vs app {size}")
    check("widget capture is NOT blank", distinct_colors(widget_png) > 1)

    # --- formats ------------------------------------------------------------
    for suffix in (".jpg", ".pdf"):
        try:
            written = app.capture(OUT / f"verify-app{suffix}")
            check(f"saves {suffix}", written.is_file() and written.stat().st_size > 0)
        except Exception as exc:  # noqa: BLE001 - reporting, not handling
            check(f"saves {suffix}", False, f"{type(exc).__name__}: {exc}")

    # --- guards -------------------------------------------------------------
    card.detach()
    app.tk.update_idletasks()
    try:
        card.capture(OUT / "verify-should-not-exist.png")
        check("detached widget raises", False, "no exception raised")
    except bs_errors.BootstackError:
        check("detached widget raises BootstackError", True)
    except Exception as exc:  # noqa: BLE001
        check("detached widget raises BootstackError", False,
              f"raised {type(exc).__name__} instead")
    card.attach()

    try:
        label.capture(OUT / "verify-should-not-exist.png", inset=9999)
        check("absurd inset raises", False, "no exception raised")
    except bs_errors.BootstackError:
        check("absurd inset raises BootstackError", True)

    # --- always-on-top is restored, both directions -------------------------
    root = app.tk
    try:
        root.attributes("-topmost", False)
        root.update_idletasks()
        app.capture(OUT / "verify-topmost-off.png")
        check("a non-topmost window is left non-topmost",
              not root.attributes("-topmost"))

        root.attributes("-topmost", True)
        root.update_idletasks()
        app.capture(OUT / "verify-topmost-on.png")
        check("a deliberately pinned window stays pinned",
              bool(root.attributes("-topmost")))
        root.attributes("-topmost", False)
    except tkinter.TclError as exc:
        skip("always-on-top is restored",
             f"window manager does not support -topmost: {exc}")

    negative_monitor_arm()
    report()
    app.close()


def negative_monitor_arm():
    """The silent trap: a region at negative coordinates grabbed as pure black.

    A window on a display placed left of or above the primary one sits at
    negative virtual-desktop coordinates. Grabbing that rectangle without
    spanning the whole desktop returns a uniformly black image and raises
    nothing. Control arm first, so a machine that cannot reproduce the trap
    says so instead of quietly "passing".
    """
    negative = [m for m in get_monitors() if m.x < 0 or m.y < 0]
    if not negative:
        skip("negative-origin monitor", "no monitor at a negative origin here")
        return

    target = negative[0]
    original = app.tk.geometry()
    app.tk.geometry(f"+{target.x + 400}+{target.y + 200}")
    app.tk.update()
    app.tk.update_idletasks()

    root = app.tk
    x, y = root.winfo_rootx(), root.winfo_rooty()
    bbox = (x, y, x + root.winfo_width(), y + root.winfo_height())

    try:
        control = ImageGrab.grab(bbox=bbox, all_screens=False)
        control_colors = distinct_colors(control)
        control.close()
    except (OSError, NotImplementedError, TypeError) as exc:
        control_colors = None
        note("negative-origin control", f"could not run the control: {exc}")

    ours = distinct_colors(app.capture(OUT / "verify-negative-monitor.png"))

    if control_colors is None:
        note("negative-origin monitor", f"capture() gave {ours} distinct colors")
    elif control_colors > 2:
        note("negative-origin monitor",
             f"this machine does NOT reproduce the trap (control had "
             f"{control_colors} colors) — comparison proves nothing")
    else:
        check("negative-origin display captures real pixels", ours > 2,
              f"control blank at {control_colors}, capture() at {ours}")

    app.tk.geometry(original)
    app.tk.update_idletasks()


def report():
    print()
    width = max(len(name) for name, _, _ in results)
    for name, status, detail in results:
        print(f"  {status}  {name:<{width}}  {detail}")
    failed = [n for n, s, _ in results if s == "FAIL"]
    passed = sum(1 for _, s, _ in results if s == "PASS")
    print(f"\n  {passed} passed, {len(failed)} failed, "
          f"{sum(1 for _, s, _ in results if s == 'SKIP')} skipped")
    if failed:
        print("  FAILED:", ", ".join(failed))
    print()


banner()

with bs.App(title="Capture verification", padding=16, gap=10,
            size=(560, 360)) as app:
    bs.Label("Capture verification", font="heading-lg")
    with bs.Card(padding=12, gap=6) as card:
        label = bs.Label("This card is captured on its own.", accent="primary")
        bs.Button("Colored content", accent="primary")
    bs.Label("Colored content above proves the grab is not blank.",
             font="caption")

app.schedule.delay(600, run_checks)
app.run()