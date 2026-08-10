"""Probe: does a click during `capture(settle=)` re-enter the handler? (#429)

`settle()` turns the event loop so the desktop can repaint, which means
anything queued runs there too — including another click on the button that
started the capture. #427's review found this by reading; nothing had ever
reproduced it.

The invariant measured here is NESTING DEPTH, not call count. A handler called
twice in a row is ordinary; a handler entered a second time while the first
call is still inside `capture()` is the defect. Depth is what tells them apart,
and it is what a fix has to move.

MEASURED, and the reason `settle()` no longer turns the event loop:

  before the fix   arm 1 depth 2, arm 3 depth 2   (re-entered mid-capture)
  after the fix    every arm depth 1, calls 2     (serialized, nothing lost)

`calls=2` after the fix is the half worth keeping in view — the second click is
not swallowed, it just waits its turn, so the person clicking still gets what
they asked for and never sees a stacked dialog.

Three arms, each printing PASS/FAIL against the FIXED behavior:

  1. guard   — a queued call lands during a 0.3s settle. Expect depth 1;
     depth 2 means the re-entrancy is back.
  2. control — the same queued call lands after the capture returns. Expect
     depth 1 and calls 2. This arm is what proves arm 1 measures nesting
     rather than "the handler only ran once", and it read depth 1 both before
     and after the fix.
  3. click   — arm 1 driven by a synthesized button release, confirming real
     input takes the same path as a queued callback.

Run it on any box with a display:  py -3.12 development/probe_429_capture_reentrancy.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import bootstack as bs

OUT = Path(tempfile.gettempdir()) / "bootstack-probe-429"
OUT.mkdir(parents=True, exist_ok=True)

SETTLE = 0.3


def run_arm(name: str, *, queue_delay_ms: int, use_click: bool) -> int:
    """Return the maximum handler nesting depth observed."""
    depth = 0
    max_depth = 0
    calls = 0
    errors: list[str] = []

    with bs.App(title=f"#429 {name}", size=(360, 140), padding=12) as app:
        button = bs.Button("Export", on_click=lambda: on_export())

        def on_export() -> None:
            nonlocal depth, max_depth, calls
            calls += 1
            depth += 1
            max_depth = max(max_depth, depth)
            try:
                app.capture(OUT / f"{name}-{calls}.png", settle=SETTLE)
            except Exception as exc:  # noqa: BLE001 - the probe reports, never raises
                errors.append(f"{type(exc).__name__}: {exc}")
            finally:
                depth -= 1

        def fire_second() -> None:
            if use_click:
                # A real release over the widget is what runs a ttk command.
                inner = button._internal
                inner.event_generate("<Button-1>", x=5, y=5)
                inner.event_generate("<ButtonRelease-1>", x=5, y=5)
            else:
                on_export()

        def start() -> None:
            # Queue the second invocation, then start the first capture. The
            # delay decides whether it lands inside the settle window or after
            # it, which is the only difference between arms 1 and 2.
            app.tk.after(queue_delay_ms, fire_second)
            on_export()

        app.tk.after(400, start)
        app.tk.after(int(SETTLE * 1000) + 2500, app.close)

    app.run()

    verdict = "re-entered" if max_depth > 1 else "not re-entered"
    print(f"  calls={calls}  max_depth={max_depth}  ({verdict})")
    for err in errors:
        print(f"  error: {err}")
    return max_depth


def main() -> int:
    print(f"platform={sys.platform}  settle={SETTLE}s  out={OUT}")
    failures = 0

    print("\n[1] guard — second call queued INSIDE the settle window")
    depth = run_arm("repro", queue_delay_ms=100, use_click=False)
    if depth == 1:
        print("  PASS - settling did not dispatch it; no re-entry (was depth 2)")
    else:
        print("  FAIL - #429 is back: the handler re-entered during settle()")
        failures += 1

    print("\n[2] control — same call queued AFTER the capture returns")
    depth = run_arm("control", queue_delay_ms=int(SETTLE * 1000) + 900,
                    use_click=False)
    if depth == 1:
        print("  PASS - two sequential calls, no nesting (arm 1 measures nesting)")
    else:
        print(f"  FAIL - control nested at depth {depth}; arm 1 proves nothing")
        failures += 1

    print("\n[3] click — a synthesized button release inside the settle window")
    depth = run_arm("click", queue_delay_ms=100, use_click=True)
    if depth == 1:
        print("  PASS - real input waits its turn too (was depth 2)")
    else:
        print("  FAIL - a real click still re-enters mid-capture")
        failures += 1

    print(f"\n{'FAILURES: ' + str(failures) if failures else 'all arms as expected'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
