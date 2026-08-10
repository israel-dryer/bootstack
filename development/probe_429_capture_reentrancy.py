"""Probe: does a click during `capture(settle=)` re-enter the handler? (#429)

`settle()` turns the event loop so the desktop can repaint, which means
anything queued runs there too — including another click on the button that
started the capture. #427's review found this by reading; nothing had ever
reproduced it.

The invariant measured here is NESTING DEPTH, not call count. A handler called
twice in a row is ordinary; a handler entered a second time while the first
call is still inside `capture()` is the defect. Depth is what tells them apart,
and it is what a fix has to move.

⚠ THIS PROBE'S EXPECTATIONS WERE WRITTEN AGAINST A FIX THAT WAS REVERSED, AND
NEITHER OF ITS RE-ENTRY ARMS TESTS WHAT NOW GUARDS THE CAPTURE. Settling was
briefly changed to dispatch nothing at all, and both arms below were tuned to
that. It could not stay: on macOS the area a closed dialog uncovers is never
repainted without dispatch, so the capture photographed the dismissed dialog —
51400 of 60800 pixels wrong, through the public method. Settling dispatches
again, and blocks INPUT with `tk busy` for the duration instead. See
`probe_429_settle_without_input.py`.

What that means for each arm here, all of it measured:

  arm 1 drives the handler from a TIMER, and `tk busy` blocks input, not
  scheduled work — so it re-enters, at depth 2, by design rather than by
  defect. It is kept because that is the honest limitation of the guard: a
  capture started from a timer can overlap one already running.

  arm 3 synthesizes a click, which cannot test the guard at all —
  `event_generate` aimed at a widget delivers straight to its bindings and
  never consults the busy window, so it re-enters whether busy is held or not,
  with `tk busy status` reading 1 at the time.

The one question this probe was built for — does a REAL second click re-enter —
is now a manual check: `development/demo_429_busy_during_settle.py`.

The invariant measured is NESTING DEPTH, not call count. A handler called twice
in a row is ordinary; a handler entered a second time while the first call is
still inside `capture()` is the defect. Depth is what tells them apart.

Three arms:

  1. scheduled — a queued call lands during a 0.3s settle. Depth 2 EXPECTED:
     the guard is on input, and a timer is not input.
  2. control   — the same queued call lands after the capture returns. Expect
     depth 1 and calls 2. This arm is what proves arm 1 measures nesting
     rather than "the handler only ran once".
  3. synthetic click — depth 2 EXPECTED, and it says nothing about the guard.

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

    print("\n[1] scheduled — second call queued INSIDE the settle window")
    depth = run_arm("repro", queue_delay_ms=100, use_click=False)
    if depth > 1:
        print("  AS EXPECTED - a timer re-enters; the guard is on input, and "
              "scheduled work is not input. This is the guard's known limit.")
    else:
        print("  UNEXPECTED - a timer did not re-enter. Either settling "
              "stopped dispatching (which breaks the repaint — see "
              "probe_429_settle_without_input.py) or the timer never fired.")
        failures += 1

    print("\n[2] control — same call queued AFTER the capture returns")
    depth = run_arm("control", queue_delay_ms=int(SETTLE * 1000) + 900,
                    use_click=False)
    if depth == 1:
        print("  PASS - two sequential calls, no nesting (arm 1 measures nesting)")
    else:
        print(f"  FAIL - control nested at depth {depth}; arm 1 proves nothing")
        failures += 1

    print("\n[3] synthetic click — a button release inside the settle window")
    depth = run_arm("click", queue_delay_ms=100, use_click=True)
    if depth > 1:
        print("  AS EXPECTED - and it proves nothing about the guard: a "
              "synthesized click bypasses the busy window entirely. Whether a "
              "REAL click is swallowed is manual — "
              "development/demo_429_busy_during_settle.py")
    else:
        print("  UNEXPECTED - check the click fired at all before reading "
              "this as the guard working; it cannot be what stopped it.")
        failures += 1

    print(f"\n{'FAILURES: ' + str(failures) if failures else 'all arms as expected'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
