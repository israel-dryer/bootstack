"""Probe: does the #426 legacy-kwarg message name the RIGHT remedy?

Round-2 control for the 0.3.1 review. Round 1 gave
`_reject_legacy_child_kwargs` an `advice` parameter defaulting to
`FLEX_CHILD_ADVICE`, which recommends `grow=`. That is correct for a flex child
and WRONG for a grid cell, where `grow=` is filtered out by `GRID_KEYS` and does
nothing -- the same silent no-op #426 was filed about. Four of the nine callers
never passed the grid advice, so the defect outlived its own fix in them; the
parameter is required now, which is what this probe pins.

Each arm reports three things:

    kind    the noun the message uses ("grid cell" or "flex child")
    grow?   whether the advice recommends `grow=`
    honored whether `grow=` actually reaches the placement

An arm FAILS when the message recommends `grow=` and the container drops it.
The two control arms pin the ends: a real `Grid` (already correct) and a
`Card` in its default column mode (flex, so `grow=` is genuinely the remedy).

Measured transition (round 2 of the 0.3.1 review):

    pre-fix  at d4f2d127   arms passed 2/5 -- Card/GroupBox/AccordionSection in
                           grid mode all said "flex child" and advised grow=,
                           while recording placement options {'sticky': 'ewns'}
    post-fix               arms passed 5/5

Run: py -3.12 development/probe_426_grid_cell_advice.py
"""

import bootstack as bs
from bootstack.errors import BootstackError


def ascii_only(text):
    """The messages carry em-dashes; this console is cp1252."""
    return (text or "").encode("ascii", "replace").decode("ascii")


def message_for(make_container):
    """Return the rejection message a legacy `fill=` produces in the container."""
    container = make_container()
    try:
        bs.Label("legacy", parent=container, fill="x")
    except BootstackError as exc:
        return container, str(exc)
    return container, None


def grow_honored(container):
    """Does `grow=` on a child of this container reach the placement?"""
    child = bs.Label("grow", parent=container, grow=1)
    placement = getattr(child, "_placement", None)
    options = dict(placement.options) if placement is not None else {}
    # A flex placement carries the resolved grow weight; a grid placement has
    # already filtered the kwarg away by the time it is recorded.
    method = placement.method if placement is not None else "?"
    return method, options


def run_arm(label, make_container, *, expect_kind, expect_grow_advice):
    container, message = message_for(make_container)
    if message is None:
        print(f"[FAIL] {label}: fill= raised nothing at all")
        return False

    kind = "grid cell" if "grid cell" in message else (
        "flex child" if "flex child" in message else "?"
    )
    advises_grow = "grow=" in message
    method, options = grow_honored(container)
    honored = any(k in options for k in ("grow", "weight"))

    verdict = "PASS" if (kind == expect_kind and advises_grow == expect_grow_advice) else "FAIL"
    print(f"[{verdict}] {label}")
    print(f"        kind={kind!r} advises grow=? {advises_grow}")
    print(f"        placement={method} options={options} grow honored? {honored}")
    if advises_grow and not honored:
        print("        ^^ message recommends grow=, container drops it (this IS #426)")
    print(f"        msg: {ascii_only(message)}")
    return verdict == "PASS"


with bs.App(title="probe 426") as app:
    print("== controls ==")
    results = [
        run_arm(
            "CONTROL Grid(columns=2) -- already fixed",
            lambda: bs.Grid(columns=2),
            expect_kind="grid cell",
            expect_grow_advice=False,
        ),
        run_arm(
            "CONTROL Card() default column -- flex, grow= is real",
            lambda: bs.Card(),
            expect_kind="flex child",
            expect_grow_advice=True,
        ),
    ]

    print("== the four call sites the fix missed ==")
    results += [
        run_arm(
            "Card(layout='grid')",
            lambda: bs.Card(layout="grid", columns=2),
            expect_kind="grid cell",
            expect_grow_advice=False,
        ),
        run_arm(
            "GroupBox(layout='grid')",
            lambda: bs.GroupBox("box", layout="grid", columns=2),
            expect_kind="grid cell",
            expect_grow_advice=False,
        ),
        run_arm(
            "Accordion.add(layout='grid')",
            lambda: bs.Accordion().add("sec", layout="grid", columns=2),
            expect_kind="grid cell",
            expect_grow_advice=False,
        ),
    ]

    print("== wording: which container does the grid advice point at? ==")
    tabs = bs.Tabs()
    page = tabs.add("tab", layout="grid", columns=2)
    _, tab_message = message_for(lambda: page)
    print(f"        TabPage msg: {ascii_only(tab_message)}")
    names_grid_class = "Grid's" in (tab_message or "")
    print(f"        points at \"the Grid's columns/rows\"? {names_grid_class}"
          " (TabPage has no Grid to configure)")

print()
print(f"arms passed: {sum(results)}/{len(results)}")
