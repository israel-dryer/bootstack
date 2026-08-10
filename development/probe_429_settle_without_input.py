"""Probe: can settle() wait WITHOUT dispatching input, and still repaint? (#429)

`settle()` runs `root.update()` in its wait loop. That is what lets a queued
click re-enter the handler (#429) — and it is also what the current docstring
promises ("the interface stays responsive while this waits"). The promise is
the bug.

The alternative is to flush our own drawing and then simply sleep. No input is
dispatched, so an impatient second click waits its turn instead of stacking a
second save dialog on the end user. The question is whether the capture is
still CORRECT: the area a just-closed dialog uncovered has to be repainted
before the pixels are read, and repaint may need event processing we would no
longer be doing.

⚠ EVERY COMPARED CAPTURE COMES FROM ONE APP INSTANCE. An earlier version of
this probe took each arm from its own `bs.App` and read a 59,988-pixel
difference as a dirty capture. It was the theme: the FIRST app in a process
renders its content white, and every later app in the same process falls back
to default grey, so ~99% of pixels differ for reasons having nothing to do
with what is being measured. Two same-population shots agreed to 14 px, which
made the bogus control look sound. Same family as the repo's
"measure within one process" rule, one notch stricter.

Arms, all captured from the same window and compared against a reference shot
of it with nothing ever placed over it:

  ref     — the yardstick.
  update  — a window is closed just before the shot; settle uses update().
            The CONTROL: today's behavior must come back clean, or the
            scenario is broken and the sleep-only arm proves nothing.
  sleep   — the same, with a sleep-only settle. Clean means repaint does not
            need us to pump the loop.
  busy    — `tk busy hold` in force during the shot, to settle whether the
            busy window is photographed.

Then the point of the whole exercise: a click arriving during a sleep-only
settle, which must NOT re-enter the handler.

Run:  py -3.12 development/probe_429_settle_without_input.py
"""

from __future__ import annotations

import sys
import tempfile
import time
import tkinter
from pathlib import Path

from PIL import Image, ImageChops

import bootstack as bs
from bootstack._core import capture as _capture

OUT = Path(tempfile.gettempdir()) / "bootstack-probe-429-settle"
OUT.mkdir(parents=True, exist_ok=True)

SETTLE = 0.3
# Two captures of an unchanged window are not bit-identical; this is the floor
# arm `ref2` measures rather than assumes.
results: list[tuple[str, str]] = []


def settle_sleep_only(tk_widget, seconds: float) -> None:
    """Flush our own drawing, then wait without dispatching anything."""
    root = tk_widget._root()
    root.update_idletasks()
    time.sleep(max(seconds, 0.0))
    root.update_idletasks()


def shoot(app, name: str, settle_fn=_capture.settle) -> Path:
    """capture() with the settle step swapped out."""
    target = app._internal
    with _capture.raised(target):
        settle_fn(target, SETTLE)
        return _capture.capture_region(
            _capture.widget_region(target, 0), OUT / f"{name}.png"
        )


def differing_pixels(a: Path, b: Path) -> int:
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert("RGB"), ib.convert("RGB")
        if ia.size != ib.size:
            return -1
        diff = ImageChops.difference(ia, ib)
        return sum(1 for px in diff.getdata() if px != (0, 0, 0))


def cover_then_close(app, hold_ms: int = 250) -> None:
    """Put a window over the app and close it, the way a save dialog does."""
    top = tkinter.Toplevel(app._internal)
    top.overrideredirect(True)
    top.configure(background="#ff00ff")
    x, y = app._internal.winfo_rootx(), app._internal.winfo_rooty()
    w, h = app._internal.winfo_width(), app._internal.winfo_height()
    top.geometry(f"{w}x{h}+{x}+{y}")
    top.lift()
    top.attributes("-topmost", True)
    app.tk.update()
    time.sleep(hold_ms / 1000)
    top.destroy()


def judge(label: str, diff: int, floor: int) -> None:
    if diff < 0:
        results.append((label, "INCONCLUSIVE - sizes differ"))
    elif diff <= floor:
        results.append((label, f"PASS - {diff} px vs a {floor} px floor"))
    else:
        results.append((label, f"FAIL - {diff} px vs a {floor} px floor"))


def main() -> int:
    print(f"platform={sys.platform}  settle={SETTLE}s  out={OUT}")
    depth = 0
    max_depth = 0

    with bs.App(title="#429 settle", size=(380, 160), padding=12) as app:
        bs.Label("Capture target", font="heading-md")
        button = bs.Button("Export", on_click=lambda: on_click_capture())

        def on_click_capture() -> None:
            nonlocal depth, max_depth
            depth += 1
            max_depth = max(max_depth, depth)
            try:
                shoot(app, f"reentry-{max_depth}-{depth}", settle_sleep_only)
            finally:
                depth -= 1

        def fire_second() -> None:
            inner = button._internal
            inner.event_generate("<Button-1>", x=5, y=5)
            inner.event_generate("<ButtonRelease-1>", x=5, y=5)

        def sequence() -> None:
            ref = shoot(app, "ref")
            ref2 = shoot(app, "ref2")
            floor = max(differing_pixels(ref, ref2), 50)
            results.append(("noise floor", f"{floor} px between two ref shots"))

            cover_then_close(app)
            judge("control: update() settle after a window closed",
                  differing_pixels(ref, shoot(app, "update")), floor)

            cover_then_close(app)
            judge("test: sleep-only settle after a window closed",
                  differing_pixels(ref, shoot(app, "sleep", settle_sleep_only)),
                  floor)

            top = app._internal.winfo_toplevel()
            try:
                top.tk.call("tk", "busy", "hold", top._w, "-cursor", "watch")
                busy_shot = shoot(app, "busy")
                top.tk.call("tk", "busy", "forget", top._w)
                judge("tk busy held during the shot",
                      differing_pixels(ref, busy_shot), floor)
            except tkinter.TclError as exc:
                results.append(("tk busy", f"unavailable - {exc}"))

            # The point of the change: a click during a sleep-only settle.
            app.tk.after(100, fire_second)
            on_click_capture()

        app.tk.after(600, sequence)
        app.tk.after(9000, app.close)

    app.run()

    print()
    for label, verdict in results:
        print(f"  {label}: {verdict}")
    reentry_ok = max_depth == 1
    print(f"  click during a sleep-only settle: max_depth={max_depth} "
          f"{'PASS - did not re-enter' if reentry_ok else 'FAIL - re-entered'}")

    failures = [v for _, v in results if v.startswith("FAIL")]
    if not reentry_ok:
        failures.append("reentry")
    print(f"\n{'FAILURES: ' + str(len(failures)) if failures else 'all arms as expected'}")
    print(f"images in {OUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
