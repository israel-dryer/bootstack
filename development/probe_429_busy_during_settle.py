"""Probe: can `tk busy` swallow input during settle() without spoiling the shot?

#429's real cost is an end-user one — an impatient second click during
`capture(settle=)` re-enters the handler and stacks a second save dialog. Any
fix that lives in `capture()` itself is too late, because the developer's
handler opens that dialog BEFORE it calls capture. The only place the framework
can fix it for the end user is to stop the click being dispatched at all.

`tk busy hold` is the candidate. It has to clear two bars, and failing either
one rules it out:

  1. It must swallow a click that arrives during the settle window.
  2. It must be INVISIBLE to the capture. A busy window sits over the target,
     and the whole point of this feature is photographing that target.

Arm 3 is the control for arm 2: two captures of the same unchanged window with
busy OFF, to establish how much two shots of identical content differ on their
own. Without it, "the busy shot differs by N pixels" means nothing.

Run:  py -3.12 development/probe_429_busy_during_settle.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

import bootstack as bs

OUT = Path(tempfile.gettempdir()) / "bootstack-probe-429-busy"
OUT.mkdir(parents=True, exist_ok=True)

SETTLE = 0.3


def busy_supported(widget) -> bool:
    """Whether `tk busy` exists, asked without destroying anything.

    Checked on a live app rather than a throwaway one: tearing a root down
    takes the named fonts with it, and every later app in the process then
    fails to build a button.
    """
    try:
        widget.winfo_toplevel().tk.call(
            "tk", "busy", "status", widget.winfo_toplevel()._w
        )
        return True
    except Exception:  # noqa: BLE001 - probing for the command's existence
        return False


def differing_pixels(a: Path, b: Path) -> tuple[int, str]:
    """Count pixels that differ between two captures."""
    with Image.open(a) as ia, Image.open(b) as ib:
        ia, ib = ia.convert("RGB"), ib.convert("RGB")
        if ia.size != ib.size:
            return -1, f"different sizes {ia.size} vs {ib.size}"
        diff = ImageChops.difference(ia, ib)
        count = sum(1 for px in diff.getdata() if px != (0, 0, 0))
        return count, f"{ia.size[0]}x{ia.size[1]}"


def run_arm(name: str, *, use_busy: bool, click: bool) -> tuple[int, Path]:
    """Return (max handler nesting depth, captured path)."""
    depth = 0
    max_depth = 0
    calls = 0
    written: list[Path] = []
    notes: list[str] = []

    with bs.App(title=f"#429 busy {name}", size=(380, 160), padding=12) as app:
        bs.Label("Capture target", font="heading-md")
        button = bs.Button("Export", on_click=lambda: on_export())

        def on_export() -> None:
            nonlocal depth, max_depth, calls
            calls += 1
            depth += 1
            max_depth = max(max_depth, depth)
            target = app._internal
            held = False
            if calls == 1:
                notes.append(f"tk busy available: {busy_supported(target)}")
            try:
                if use_busy:
                    try:
                        top = target.winfo_toplevel()
                        top.tk.call("tk", "busy", "hold", top._w, "-cursor",
                                    "watch")
                        held = True
                    except Exception as exc:  # noqa: BLE001
                        notes.append(f"busy hold failed: {exc}")
                written.append(app.capture(OUT / f"{name}-{calls}.png",
                                           settle=SETTLE))
            except Exception as exc:  # noqa: BLE001 - the probe reports
                notes.append(f"{type(exc).__name__}: {exc}")
            finally:
                if held:
                    try:
                        top.tk.call("tk", "busy", "forget", top._w)
                    except Exception as exc:  # noqa: BLE001
                        notes.append(f"busy forget failed: {exc}")
                depth -= 1

        def fire_second() -> None:
            inner = button._internal
            inner.event_generate("<Button-1>", x=5, y=5)
            inner.event_generate("<ButtonRelease-1>", x=5, y=5)

        def start() -> None:
            if click:
                app.tk.after(100, fire_second)
            on_export()

        app.tk.after(400, start)
        app.tk.after(int(SETTLE * 1000) + 2500, app.close)

    app.run()

    for note in notes:
        print(f"  note: {note}")
    print(f"  calls={calls}  max_depth={max_depth}")
    return max_depth, (written[0] if written else Path())


def main() -> int:
    print(f"platform={sys.platform}  settle={SETTLE}s  out={OUT}")
    failures = 0

    print("\n[1] busy ON, click during settle - does it swallow the click?")
    depth, busy_shot = run_arm("busy", use_busy=True, click=True)
    if depth == 1:
        print("  PASS - the click did not re-enter the handler")
    else:
        print(f"  FAIL - re-entered at depth {depth}; busy did not block it")
        failures += 1

    print("\n[2] busy OFF, click during settle - the control for arm 1")
    depth, plain_shot = run_arm("plain", use_busy=False, click=True)
    if depth > 1:
        print("  PASS - re-enters without busy, so arm 1 measures the guard")
    else:
        print("  FAIL - no re-entry without busy either; arm 1 proves nothing")
        failures += 1

    print("\n[3] is the busy window visible in the photograph?")
    _, baseline_a = run_arm("baseline-a", use_busy=False, click=False)
    _, baseline_b = run_arm("baseline-b", use_busy=False, click=False)
    noise, size_a = differing_pixels(baseline_a, baseline_b)
    print(f"  control: two busy-OFF captures differ by {noise} px ({size_a})")
    signal, size_b = differing_pixels(baseline_a, busy_shot)
    print(f"  test:    busy-ON vs busy-OFF differ by {signal} px ({size_b})")
    if signal < 0 or noise < 0:
        print("  INCONCLUSIVE - captures are different sizes; compare by hand")
    elif signal <= max(noise, 0) :
        print("  PASS - busy is invisible to the capture (within its own noise)")
    else:
        print(f"  FAIL - busy changes the photograph by {signal - noise} px "
              f"beyond noise; inspect {busy_shot}")
        failures += 1

    print(f"\n{'FAILURES: ' + str(failures) if failures else 'all arms as expected'}")
    print(f"images in {OUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
