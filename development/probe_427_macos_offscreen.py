"""Why all eight capture tests fail on macOS (#427).

The shared-root suite stacks widgets past the bottom of a 1470x956 display,
so every capture test asks for a region at y ~= 2810-2990 — entirely off the
screen. What happens next is the finding: `screencapture -R` writes no valid
PNG for an off-screen region, Pillow raises `UnidentifiedImageError`, and
because that is a subclass of `OSError` the capture module reads it as
"ImageGrab is unavailable on this platform" and falls through to the Linux
subprocess chain. None of those tools exist on a Mac, so the user is told to
install `grim` — on a machine whose built-in `screencapture` works perfectly.

Every arm carries a control, so a machine that cannot reproduce the trap says
so rather than quietly agreeing.

Run: python development/probe_427_macos_offscreen.py
"""

import sys
import tkinter
from pathlib import Path

from PIL import Image, ImageGrab, UnidentifiedImageError
from screeninfo import get_monitors

import bootstack as bs
from bootstack import errors as bs_errors
from bootstack._core import capture as cap

OUT = Path(__file__).parent / "screencap_out"
OUT.mkdir(parents=True, exist_ok=True)
results = []


def line(label, detail):
    results.append((label, detail))
    print(f"  {label:<46} {detail}")


def run():
    monitor = get_monitors()[0]
    print(f"\n  display: {monitor.width}x{monitor.height} logical\n")

    # --- mechanism: is UnidentifiedImageError swallowed as OSError? ---------
    line("UnidentifiedImageError is an OSError",
         issubclass(UnidentifiedImageError, OSError))
    line("...so the missing-backend except catches it",
         "yes — which is why the region has to be diagnosed separately")
    line("capture module can read the display layout",
         cap._covered_by_a_display((0, 0, 10, 10)) is not None)

    # --- ARM 1 (control): an on-screen widget captures fine -----------------
    root = app.tk
    root.geometry("+80+80")
    root.update()
    cap.settle(root, 0.2)
    try:
        on_screen = card.capture(OUT / "probe-onscreen.png")
        with Image.open(on_screen) as img:
            line("CONTROL on-screen capture", f"OK {img.size}")
        control_ok = True
    except Exception as exc:  # noqa: BLE001 - reporting, not handling
        line("CONTROL on-screen capture", f"{type(exc).__name__}: {exc}")
        control_ok = False

    if not control_ok:
        line("VERDICT", "control failed — the rest proves nothing")
        report()
        return

    # --- ARM 2: the exact region the suite asks for ------------------------
    offscreen_bbox = (97, 2810, 170, 2830)
    try:
        ImageGrab.grab(bbox=offscreen_bbox, all_screens=True)
        line("raw ImageGrab on the suite's bbox", "returned an image (no trap)")
    except Exception as exc:  # noqa: BLE001
        line("raw ImageGrab on the suite's bbox", f"{type(exc).__name__}")

    try:
        cap.capture_region(offscreen_bbox, OUT / "probe-offscreen.png")
        line("capture_region on that bbox", "succeeded (no trap here)")
    except bs_errors.BootstackError as exc:
        first = str(exc).split("—")[0].strip().rstrip(".")
        line("capture_region on that bbox", f"BootstackError: {first}")
        line("  ^ message mentions Linux-only tools",
             "grim" in str(exc) or "XCB" in str(exc))
    except Exception as exc:  # noqa: BLE001
        line("capture_region on that bbox", f"{type(exc).__name__}: {exc}")

    # --- ARM 3: a real window dragged below the screen ---------------------
    # The user-reachable version of the same thing: no test harness involved.
    root.geometry(f"+120+{monitor.height + 200}")
    root.update()
    cap.settle(root, 0.3)
    line("window moved to y", root.winfo_rooty())
    try:
        app.capture(OUT / "probe-window-offscreen.png")
        line("capture() on an off-screen window", "succeeded")
    except bs_errors.BootstackError as exc:
        first = str(exc).split("—")[0].strip().rstrip(".")
        line("capture() on an off-screen window", f"BootstackError: {first}")
    except Exception as exc:  # noqa: BLE001
        line("capture() on an off-screen window", f"{type(exc).__name__}: {exc}")

    # --- ARM 4: half off the bottom edge -----------------------------------
    root.geometry(f"+140+{monitor.height - 120}")
    root.update()
    cap.settle(root, 0.3)
    try:
        partial = app.capture(OUT / "probe-window-partial.png")
        with Image.open(partial) as img:
            line("capture() on a half-off-screen window", f"OK {img.size}")
    except Exception as exc:  # noqa: BLE001
        line("capture() on a half-off-screen window",
             f"{type(exc).__name__}: {str(exc).split('—')[0].strip()}")

    # --- ARM 5: is screencapture itself fine? ------------------------------
    # Proves the platform tool works and only the region was the problem.
    import shutil
    line("screencapture on PATH", bool(shutil.which("screencapture")))
    line("no Linux backend installed",
         not any(shutil.which(n) for n, _ in cap._SUBPROCESS_BACKENDS))

    root.geometry("+80+80")
    root.update()
    report()


def report():
    print(f"\n  {len(results)} measurements\n")
    app.close()


if sys.platform != "darwin":
    print("This probe measures the macOS path; run it on a Mac.")
    raise SystemExit(0)

print(f"\n  tk {tkinter.TkVersion}  pillow {Image.__version__}")

with bs.App(title="Off-screen capture probe", padding=16, gap=10,
            size=(480, 300)) as app:
    bs.Label("Off-screen capture probe", font="heading-lg")
    with bs.Card(padding=12, gap=6) as card:
        bs.Label("Card content", accent="primary")
        bs.Button("Colored", accent="primary")

app.schedule.delay(600, run)
app.run()