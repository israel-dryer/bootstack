"""Manual demo: does `tk busy` swallow a REAL click during settle? (#429)

⚠ THIS ONE NEEDS A HUMAN. It is the only arm of #429 that cannot be automated,
and the reason is worth stating so nobody replaces it with a probe:

    `tk busy` intercepts input by putting a window over the target, so it only
    ever sees events the window system routed by pointer position.
    `event_generate` aimed at a widget delivers straight to that widget's
    bindings and never consults the busy window at all. A synthesized click
    therefore re-enters the handler whether busy is held or not — measured,
    with `tk busy status` reading 1 at the time. Any automated version of this
    check is a false negative waiting to happen.

`tests/widgets/public/test_capture.py` covers the halves that CAN be asserted:
that settling repaints the area a closed window uncovered, and that the window
is held busy while it dispatches. What is left for a person is whether that
hold actually stops a click.

WHAT TO DO

  1. Run it.
  2. Click "Export" ONCE, then immediately click it again two or three more
     times, as fast as you can — an impatient user who thinks nothing
     happened. The capture takes about a second and a half, deliberately, so
     there is a wide window to click into.
  3. Read the log in the window.

WHAT YOU SHOULD SEE — AND IT DEPENDS ON THE PLATFORM

  captures started: 1        <- every extra click was swallowed
  max nesting:      1        <- the handler never re-entered itself

  Expected where the toolkit honors `tk busy`: X11 and Win32 map the busy
  window, so the click lands on it and is discarded.

WHAT macOS DOES, AND IT IS NOT A REGRESSION

  captures started: 3
  max nesting:      2        <- a click landed INSIDE the running capture

  ⚠ MEASURED AND EXPECTED ON AQUA. `tk busy hold` there reports success and
  never maps the window it created — `tk busy status` returns 1 while the busy
  window sits at `winfo_ismapped() == 0`, and Tk's own hit test at the button
  still resolves to the button. Reproduced in plain tkinter on Tk 8.6.17, so
  it is the toolkit, not the framework. Run arm 0 of
  `probe_429_busy_during_settle.py` to see what THIS box does before reading
  a re-entry here as a defect.

Nesting above 1 on a platform whose arm 0 says the hold IS real is the defect
in #429: for a real application that second click opens a second save dialog
on top of the first, and starts an overlapping capture nobody asked for.

The demo captures to a temporary directory and deletes nothing, so the images
are there if you want to confirm the picture is of the window rather than of a
dialog left over the top of it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import bootstack as bs

OUT = Path(tempfile.gettempdir()) / "bootstack-demo-429-busy"
OUT.mkdir(parents=True, exist_ok=True)

# Long enough that a person can comfortably click into the settle window.
SETTLE = 1.5


def main() -> int:
    started = 0
    finished = 0
    depth = 0
    max_depth = 0

    with bs.App(title="#429 — click Export repeatedly", size=(520, 360),
                padding=16, gap=8) as app:
        bs.Label("Click Export once, then keep clicking",
                 font="heading-md")
        bs.Label(
            f"The capture pauses for {SETTLE}s on purpose. Extra clicks during "
            f"that pause should be swallowed.",
            font="caption",
        )
        log = bs.TextArea(height=12, read_only=True)
        lines: list[str] = []

        def note(message: str) -> None:
            # The tail is rewritten rather than appended to: there is no public
            # way to scroll a TextArea, so a plain append would push the newest
            # line out of sight exactly when it matters.
            lines.append(message)
            log.value = "\n".join(lines[-12:])

        def on_export() -> None:
            nonlocal started, finished, depth, max_depth
            started += 1
            depth += 1
            max_depth = max(max_depth, depth)
            mine = started
            note(f"[{mine}] capture started   (nesting now {depth})")
            try:
                app.capture(OUT / f"shot-{mine}.png", settle=SETTLE)
                finished += 1
                note(f"[{mine}] capture finished")
            except Exception as exc:              # noqa: BLE001 - demo surface
                note(f"[{mine}] capture FAILED: {type(exc).__name__}: {exc}")
            finally:
                depth -= 1

        def hold_is_real() -> bool:
            """Does `tk busy` actually block input on THIS box?

            `tk busy status` is not the answer — macOS returns 1 for a busy
            window it never maps. What settles it is whether that window is
            mapped and whether Tk's hit test at the button resolves to it.
            """
            top = app._internal.winfo_toplevel()
            inner = export_button._internal
            x, y = inner.winfo_rootx() + 5, inner.winfo_rooty() + 5
            try:
                top.tk.call("tk", "busy", "hold", top._w)
                app.tk.update()
                mapped = any(
                    str(top.tk.call("winfo", "ismapped", str(w))) == "1"
                    for w in top.tk.splitlist(
                        top.tk.call("winfo", "children", top._w))
                    if "Busy" in str(w)
                )
                hit = str(top.tk.call("winfo", "containing", x, y))
                return mapped and hit != str(inner)
            except Exception:                     # noqa: BLE001 - demo surface
                return False
            finally:
                try:
                    top.tk.call("tk", "busy", "forget", top._w)
                    app.tk.update()
                except Exception:                 # noqa: BLE001
                    pass

        def report() -> None:
            real = hold_is_real()
            note("")
            note("---- verdict " + "-" * 30)
            note(f"captures started: {started}")
            note(f"captures finished: {finished}")
            note(f"max nesting:      {max_depth}")
            note(f"tk busy honored here: {'yes' if real else 'NO'}")
            if started == 0:
                note("NOTHING CLICKED — click Export, then click it again fast.")
            elif max_depth > 1 and real:
                note("FAIL — this platform honors the hold and a click still")
                note("re-entered the handler mid-capture.")
            elif max_depth > 1:
                note("EXPECTED — this platform does not honor `tk busy`, so")
                note("the click was never going to be blocked. Not a")
                note("regression; it is the known limit (macOS/aqua).")
            elif started > 1:
                note("Clicks were spaced out. Click FASTER to test the guard:")
                note("the extra clicks have to land during the pause.")
            elif real:
                note("PASS — the extra clicks were swallowed.")
            else:
                note("INCONCLUSIVE — only one capture ran, and this platform")
                note("would not have blocked a click anyway. Click faster.")

        with bs.Row(gap=8):
            # Named: hold_is_real() hit-tests against this exact button.
            export_button = bs.Button("Export", accent="primary",
                                      on_click=on_export)
            bs.Button("Show verdict", on_click=report)
            bs.Button("Quit", on_click=app.close)

        note(f"platform={sys.platform}  settle={SETTLE}s")
        note(f"images -> {OUT}")
        note("")

    app.run()
    print(f"captures started={started} finished={finished} max_nesting={max_depth}")
    print(f"images in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
