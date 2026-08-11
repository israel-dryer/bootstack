"""Probe: is the `tk busy` guard held during settle, and does it spoil the shot?

#429's real cost is an end-user one — an impatient second click during
`capture(settle=)` re-enters the handler and stacks a second save dialog. Any
fix that lives in `capture()` itself is too late, because the developer's
handler opens that dialog BEFORE it calls capture. The only place the framework
can fix it for the end user is to stop the click being dispatched at all.

`tk busy hold` is what ships. Settling has to dispatch — the area a closed
window uncovers is not repainted otherwise, which is the defect
`probe_429_settle_without_input.py` records — so the guard has to block input
while the loop turns rather than by refusing to turn it.

⚠ WHAT THIS PROBE CANNOT DO, AND WHY IT NO LONGER TRIES. It used to claim it
measured whether busy SWALLOWS A CLICK. It cannot. `tk busy` intercepts input
by putting a window over the target, so it only ever sees events the window
system routed by pointer position, while `event_generate` aimed at a widget
delivers straight to that widget's bindings and never consults the busy window.
A synthesized click re-enters whether busy is held or not — arm 2 below
demonstrates exactly that, with `tk busy status` reading 1 at the time. The
earlier version read its own false negative as evidence and reported "busy did
not block it". The swallowing half is a manual check:
`development/demo_429_busy_during_settle.py`.

⚠ AND ITS CONTROL USED TO DRIFT. Arms were driven through `_capture.settle`,
so when the sleep-only version shipped the control silently became the test and
arm 2 reported "no re-entry without busy either; arm 1 proves nothing" — true,
but about the wrong thing. Strategies are pinned in this file now.

Arms:

  0. IS THE HOLD REAL ON THIS PLATFORM? `tk busy status` is not the answer —
     macOS returns 1 for a busy window it never maps. The answer is whether
     that window is MAPPED and whether Tk's own hit test at a button inside
     the target resolves to it or to the button. This arm is the automatable
     substitute for the manual click check, and it is the arm that would have
     caught the macOS hole immediately. Measured on Tk 8.6.17/aqua:
     status=1, mapped=0, hit=the button.
  1. Is the window held busy WHILE settling dispatches? Structural, and it is
     also asserted by `tests/widgets/public/test_capture.py`.
  2. Does a synthesized click re-enter anyway? It does. Kept as the standing
     demonstration that this technique cannot answer the input question.
  3. Is the busy window visible in the photograph? Compared against a floor
     measured across a window RESTACK, not across two identical back-to-back
     grabs — the old floor was two static shots, far too tight a yardstick for
     a comparison that restacks a window, and it turned text antialiasing into
     a reported failure.

Run:  python development/probe_429_busy_during_settle.py
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops

import bootstack as bs
from bootstack._core import capture as _capture

OUT = Path(tempfile.gettempdir()) / "bootstack-probe-429-busy"
OUT.mkdir(parents=True, exist_ok=True)

SETTLE = 0.3
results: list[tuple[str, str]] = []


def settle_dispatch_no_busy(tk_widget, seconds: float) -> None:
    """Dispatch throughout, with NO busy guard — pinned, never imported.

    This is the pre-#429 shape, and it is what arm 3 compares against: the
    same dispatching behavior the shipped settle has, minus the one thing
    under test.
    """
    root = tk_widget._root()
    root.update_idletasks()
    root.update()
    deadline = time.monotonic() + max(seconds, 0.0)
    while time.monotonic() < deadline:
        time.sleep(0.01)
        root.update()


def differing_pixels(a: Path, b: Path) -> tuple[int, str]:
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert("RGB"), ib.convert("RGB")
        if ia.size != ib.size:
            return -1, f"different sizes {ia.size} vs {ib.size}"
        diff = ImageChops.difference(ia, ib)
        return (sum(1 for px in diff.getdata() if px != (0, 0, 0)),
                f"{ia.size[0]}x{ia.size[1]}")


def shoot(app, name: str, settle_fn) -> Path:
    """capture() with the settle step swapped out, and a restack first."""
    target = app._internal
    with _capture.raised(target):
        settle_fn(target, SETTLE)
        return _capture.capture_region(
            _capture.widget_region(target, 0), OUT / f"{name}.png"
        )


def main() -> int:
    print(f"platform={sys.platform}  settle={SETTLE}s  out={OUT}")
    depth = 0
    max_depth = 0
    busy_seen: list[str] = []

    with bs.App(title="#429 busy", size=(380, 160), padding=12) as app:
        bs.Label("Capture target", font="heading-md")
        button = bs.Button("Export", on_click=lambda: on_export())
        top = app._internal.winfo_toplevel()

        def busy_status() -> str:
            try:
                return str(top.tk.call("tk", "busy", "status", top._w))
            except Exception as exc:            # noqa: BLE001 - probe reports
                return f"unavailable ({exc})"

        def on_export() -> None:
            nonlocal depth, max_depth
            depth += 1
            max_depth = max(max_depth, depth)
            try:
                app.capture(OUT / f"export-{max_depth}-{depth}.png",
                            settle=SETTLE)
            finally:
                depth -= 1

        def click_the_button() -> None:
            inner = button._internal
            inner.event_generate("<Button-1>", x=5, y=5)
            inner.event_generate("<ButtonRelease-1>", x=5, y=5)

        def sequence() -> None:
            nonlocal depth, max_depth

            # [0] Does the hold DO anything here? status is not evidence.
            inner = button._internal
            px, py = inner.winfo_rootx() + 5, inner.winfo_rooty() + 5
            top.tk.call("tk", "busy", "hold", top._w)
            app.tk.update()
            busy_windows = [str(w) for w in
                            top.tk.splitlist(top.tk.call("winfo", "children",
                                                         top._w))
                            if "Busy" in str(w)]
            mapped = [w for w in busy_windows
                      if str(top.tk.call("winfo", "ismapped", w)) == "1"]
            hit = str(top.tk.call("winfo", "containing", px, py))
            top.tk.call("tk", "busy", "forget", top._w)
            app.tk.update()
            if mapped and hit not in (str(inner), str(inner._w)):
                results.append((
                    "[0] is the hold real on this platform",
                    f"YES - busy window mapped and the hit test at the button "
                    f"resolves to {hit!r}; input should be blocked here"))
            else:
                results.append((
                    "[0] is the hold real on this platform",
                    f"NO - busy windows {busy_windows or 'none'}, mapped "
                    f"{mapped or 'none'}, hit test at the button resolves to "
                    f"{hit!r}. The hold is accepted and does nothing, so a "
                    f"real click re-enters. Known on macOS/aqua."))

            # [1] Is busy held while settling dispatches? Read from inside the
            # settle window by a timer, which only runs because it dispatches.
            before = busy_status()
            app.tk.after(60, lambda: busy_seen.append(busy_status()))
            app.capture(OUT / "structural.png", settle=SETTLE)
            after = busy_status()
            if busy_seen == ["1"] and before == "0" and after == "0":
                results.append(("[1] busy held while settling dispatched",
                                "PASS - 0 before, 1 during, 0 after"))
            elif not busy_seen:
                results.append(("[1] busy held while settling dispatched",
                                "FAIL - the timer never fired, so settling "
                                "dispatched nothing at all"))
            else:
                results.append(("[1] busy held while settling dispatched",
                                f"FAIL - before={before} during={busy_seen} "
                                f"after={after}"))

            # [2] The blind spot, kept deliberately.
            depth = max_depth = 0
            app.tk.after(80, click_the_button)
            on_export()
            if max_depth > 1:
                results.append((
                    "[2] synthesized click during settle",
                    f"AS EXPECTED - re-entered to depth {max_depth} WITH busy "
                    f"held; event_generate bypasses the busy window, so this "
                    f"technique cannot test the guard. Use the manual demo."))
            else:
                results.append((
                    "[2] synthesized click during settle",
                    "UNEXPECTED - did not re-enter. That is not evidence busy "
                    "worked; check the click fired at all before believing it."))

            # [3] Is the busy window visible? Floor measured across a restack.
            a = shoot(app, "floor-a", settle_dispatch_no_busy)
            b = shoot(app, "floor-b", settle_dispatch_no_busy)
            floor, size = differing_pixels(a, b)
            results.append(("[3] noise floor across a restack",
                            f"{floor} px ({size})"))
            shipped = shoot(app, "shipped", _capture.settle)
            signal, _ = differing_pixels(a, shipped)
            if signal < 0 or floor < 0:
                results.append(("[3] busy visible in the photograph?",
                                "INCONCLUSIVE - sizes differ, compare by hand"))
            elif signal <= floor:
                results.append((
                    "[3] busy visible in the photograph?",
                    f"PASS - {signal} px vs a {floor} px floor; invisible. "
                    f"READ THIS WITH ARM 0: where the hold is not real the "
                    f"window is never mapped, so invisibility is trivially "
                    f"true and says nothing about a platform that maps it."))
            else:
                results.append(("[3] busy visible in the photograph?",
                                f"FAIL - {signal} px vs a {floor} px floor; "
                                f"inspect {shipped}"))

            app.close()

        app.tk.after(600, sequence)
        app.tk.after(30000, app.close)

    app.run()

    print()
    for label, verdict in results:
        print(f"  {label}: {verdict}")
    failures = [v for _, v in results if v.startswith("FAIL")]
    print(f"\n{'FAILURES: ' + str(len(failures)) if failures else 'all arms as expected'}")
    print(f"images in {OUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
