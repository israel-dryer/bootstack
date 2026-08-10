"""Probe: can settle() wait WITHOUT dispatching input, and still repaint? (#429)

⚠ ANSWERED — NO, and this probe is kept as the record of how that was
established. On macOS the area a closed window uncovers is repainted only
while the event loop is turning. A sleep-only settle photographs the dialog
that was just dismissed: measured at 51400 of 60800 pixels wrong through the
public `capture()`, following the pattern its own docstring teaches. What
ships now dispatches, and blocks input with `tk busy` instead.

The original question was the reverse. `settle()` ran `root.update()` in its
wait loop, which is what let a queued click re-enter the handler (#429), so
the alternative was to flush our own drawing and simply sleep — no dispatch,
so an impatient second click waits its turn rather than stacking a second save
dialog. The open half was whether the capture stayed CORRECT, since repaint
might need the very event processing that removes. It does.

⚠ THE PROBE ITSELF IS THE OTHER LESSON. Its control used to call
`_capture.settle`, so when the sleep-only version shipped the control BECAME
the test — two arms running identical code, byte-identical images, and a
"control" that could no longer disagree with what it was controlling for. It
reported three FAILs that said nothing about the question. Every strategy is
now pinned in this file; only the explicitly-labeled `shipped` arm reads the
live implementation.

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
  update  — a window is closed just before the shot; settle dispatches
            throughout. The CONTROL: it must come back clean, or the scenario
            is broken and the sleep-only arm proves nothing.
  sleep   — the same, with a sleep-only settle. Expected to come back STALE:
            that is the defect, reproduced.
  shipped — the same again, through whatever `_capture.settle` currently is.
            Must match the `update` arm.
  busy    — `tk busy hold` in force during the shot, to settle whether the
            busy window is photographed. It is not.

Then a click arriving during a sleep-only settle — which shows only that such
a settle dispatches nothing. It cannot test the `tk busy` guard; see the note
at that arm.

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


# ⚠ EVERY STRATEGY BELOW IS DEFINED HERE, NOT IMPORTED FROM `_capture`.
# This probe originally took its control from `_capture.settle` itself. When
# the sleep-only change shipped, the control silently BECAME the test: both
# arms ran identical code, produced byte-identical images, and the probe went
# on reporting a "control" that could no longer fail differently from what it
# was controlling for. Pin the comparison, or it drifts with the source.
def settle_update_loop(tk_widget, seconds: float) -> None:
    """The pre-#429 settle: dispatch throughout the wait."""
    root = tk_widget._root()
    root.update_idletasks()
    root.update()
    deadline = time.monotonic() + max(seconds, 0.0)
    while time.monotonic() < deadline:
        time.sleep(0.01)
        root.update()


def settle_sleep_only(tk_widget, seconds: float) -> None:
    """The first pass at #429: flush our drawing, then wait dispatching nothing.

    ⚠ Kept as an arm rather than deleted, because it is the shape that caused
    the defect: on macOS the area a closed window uncovers is never repainted
    without dispatch, so the capture photographs the dismissed dialog.
    """
    root = tk_widget._root()
    root.update_idletasks()
    time.sleep(max(seconds, 0.0))
    root.update_idletasks()


def shoot(app, name: str, settle_fn=settle_update_loop) -> Path:
    """capture() with the settle step swapped out.

    The default is the PINNED pre-#429 strategy, never `_capture.settle` — see
    the note above the strategies.
    """
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


def judge(label: str, diff: int, floor: int, expect: str = "clean") -> None:
    """Record an arm against what it is SUPPOSED to show.

    One arm is expected to come back stale — it reproduces the defect — so a
    bare pass/fail would leave this probe reporting a failure forever and
    reading as broken. `expect` is what makes a reproduced defect a PASS and,
    just as importantly, makes a defect that stopped reproducing a FAIL.
    """
    clean = diff <= floor
    if diff < 0:
        results.append((label, "INCONCLUSIVE - sizes differ"))
    elif clean == (expect == "clean"):
        state = "clean" if clean else "stale, as it should be"
        results.append((label, f"PASS - {diff} px vs a {floor} px floor ({state})"))
    elif expect == "stale":
        results.append((label, (
            f"FAIL - {diff} px vs a {floor} px floor; this arm reproduces the "
            f"defect and it stopped reproducing, so the comparison is dead")))
    else:
        results.append((label, f"FAIL - {diff} px vs a {floor} px floor (stale)"))


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
            judge("control: dispatching settle after a window closed",
                  differing_pixels(ref, shoot(app, "update")), floor)

            cover_then_close(app)
            judge("test: sleep-only settle after a window closed",
                  differing_pixels(ref, shoot(app, "sleep", settle_sleep_only)),
                  floor, expect="stale")

            # What actually ships today, measured rather than assumed. Read
            # against the two arms above: it has to match the dispatching one.
            cover_then_close(app)
            judge("shipped: _capture.settle after a window closed",
                  differing_pixels(ref, shoot(app, "shipped", _capture.settle)),
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

            # ⚠ THIS ARM CANNOT TEST `tk busy`, and is kept only to show that
            # a sleep-only settle dispatches nothing. `event_generate` aimed
            # at a widget delivers straight to its bindings and never consults
            # the busy window, so it re-enters whether busy is held or not —
            # measured, with `tk busy status` reading 1 at the time. Whether a
            # REAL click is swallowed is a manual check:
            # development/demo_429_busy_during_settle.py
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
