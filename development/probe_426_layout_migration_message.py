"""Probe for #426 - the flex-child migration error must name kwargs that exist.

The defect was never that the error fired wrongly; it fired correctly and then
named `align_self=` / `justify_self=`, neither of which is a real kwarg. A user
who followed the advice verbatim landed on a raw `TclError` naming a Tk option
they never wrote.

So the thing worth testing is not the wording but the PROPERTY: every kwarg the
message recommends must actually construct. Arm 2 extracts the recommended
kwarg names out of the live message text and tries each one, which keeps the
probe honest if the message is reworded later.

Arm 3 is the control: it asserts the pre-fix advice (`align_self=`) is BOTH
absent from the message and genuinely broken, so a passing arm 2 cannot be an
artifact of the framework having quietly started accepting anything.

Run:  py -3.13 development/probe_426_layout_migration_message.py
"""

from __future__ import annotations

import re
import sys

import bootstack as bs

# The values the message advertises for each per-axis key, from `grid_sticky`
# in widgets/_core/container.py.
_SAMPLE_VALUE = {
    "grow": 1,
    "horizontal": "stretch",
    "vertical": "stretch",
}

failures: list[str] = []


def _ascii(text: str) -> str:
    """This box's console is cp1252; keep probe output plain ASCII."""
    return text.encode("ascii", "replace").decode("ascii")


with bs.App(title="probe_426", size=(320, 200)) as app:

    # -- Arm 1: the migration error still fires on a legacy kwarg -------------
    message = ""
    try:
        bs.Picture(fill="x")
    except Exception as exc:
        message = str(exc)
        print(f"ARM 1 [{type(exc).__name__}]: {_ascii(message)}")
    else:
        failures.append("ARM 1: fill= did not raise at all")
        print("ARM 1: FAIL - fill= constructed without raising")

    # -- Arm 2: every kwarg the message recommends must construct -------------
    # Pull `name=` tokens straight out of the live text rather than hardcoding
    # them, so a future reword is checked too.
    recommended = [k for k in re.findall(r"\b([a-z_]+)=", message)]
    recommended = [k for k in dict.fromkeys(recommended) if k not in ("for",)]
    print(f"\nARM 2: message recommends {recommended or '(nothing)'}")

    if not recommended:
        failures.append("ARM 2: message recommends no kwarg at all")
        print("ARM 2: FAIL - the message names no remedy")

    for name in recommended:
        if name not in _SAMPLE_VALUE:
            failures.append(f"ARM 2: message names {name}=, which the probe "
                            f"has no sample value for - is it a real kwarg?")
            print(f"   {name}= -> FAIL (unknown to this probe)")
            continue
        try:
            bs.Picture(**{name: _SAMPLE_VALUE[name]})
        except Exception as exc:
            failures.append(f"ARM 2: {name}= is recommended but raises "
                            f"{type(exc).__name__}: {exc}")
            print(f"   {name}={_SAMPLE_VALUE[name]!r} -> FAIL "
                  f"[{type(exc).__name__}] {_ascii(str(exc))}")
        else:
            print(f"   {name}={_SAMPLE_VALUE[name]!r} -> ok")

    # -- Arm 3: control - the pre-fix advice is absent AND still broken -------
    print("\nARM 3 (control): the pre-fix names")
    for dead in ("align_self", "justify_self"):
        if f"{dead}=" in message:
            failures.append(f"ARM 3: message still names {dead}=")
            print(f"   {dead}= still named in the message -> FAIL")
        else:
            print(f"   {dead}= not named in the message -> ok")

    try:
        bs.Picture(align_self="stretch")
    except Exception as exc:
        print(f"   align_self= still raises [{type(exc).__name__}] -> ok "
              f"(control is live)")
    else:
        # Not a failure of the fix, but it would mean arm 2 proves nothing.
        print("   align_self= now CONSTRUCTS -> control is dead; arm 2 is "
              "no longer meaningful")
        failures.append("ARM 3: align_self= constructs, so the control is dead")

print("\n" + "=" * 60)
if failures:
    print(f"FAIL ({len(failures)})")
    for f in failures:
        print(f"  - {_ascii(f)}")
    sys.exit(1)
print("PASS - every kwarg the migration error recommends constructs")
