"""Scroll-gesture coverage across Tk 8.6 and Tk 9.

Tk 9 changed the scroll-event contract and every scrolling widget shipped
code written against Tk 8.6:

- A precise-delta device — every Apple trackpad, Magic Mouse and Magic
  Trackpad — fires `<TouchpadScroll>` and never `<MouseWheel>`. Widgets
  bound only `<MouseWheel>`, so scrolling was completely dead on a Mac
  running Tk 9 (reported against Python 3.14.6 / Tcl-Tk 9.0.3).
- Wheel deltas are normalized to multiples of 120 everywhere. On Aqua a
  notch used to report 1, so the old `delta = -event.delta` scrolled 120
  units per notch instead of one.
- On X11 `<Button-4>`/`<Button-5>` are no longer delivered to scripts,
  and widgets bound *only* those there.

Normalization now lives in `bootstack._runtime.wheel`. The unit tests run
everywhere; the integration tests need a Tk that actually generates
`<TouchpadScroll>` and skip below 8.7.
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack._runtime import wheel


requires_touchpad = pytest.mark.skipif(
    not wheel.has_touchpad_scroll(),
    reason="Tk < 8.7 does not generate <TouchpadScroll>",
)


class _FakeEvent:
    """Minimal stand-in so notch math is testable without a windowing system."""

    def __init__(self, delta=0, num=None):
        self.delta = delta
        self.num = num


def _packed(dx: int, dy: int) -> int:
    """Pack precise deltas the way Tk does, for `event_generate(delta=...)`.

    A positive `dy` scrolls toward the start of the content, so tests that
    start at the top pass a negative one.
    """
    return ((dx & 0xFFFF) << 16) | (dy & 0xFFFF)


# --- wheel notch normalization -------------------------------------------


legacy_aqua = pytest.mark.skipif(
    wheel.has_touchpad_scroll(),
    reason="Tk 8.7+ normalizes Aqua deltas to multiples of 120",
)


@requires_touchpad
@pytest.mark.parametrize(
    "delta, expected",
    [(120, 1.0), (-120, -1.0), (240, 2.0), (60, 0.5), (0, 0.0)],
)
def test_wheel_notches_normalizes_delta(app, delta, expected):
    """On Tk 8.7+ every platform reports one notch as 120."""
    assert wheel.wheel_notches(app._tk_root, _FakeEvent(delta=delta)) == expected


@legacy_aqua
@pytest.mark.parametrize("delta, expected", [(1, 1.0), (-1, -1.0), (3, 3.0)])
def test_wheel_notches_reads_legacy_aqua_delta(app, delta, expected):
    """Tk 8.6 on Aqua reported one notch as 1, and still must read as 1.0.

    Skipped off legacy Aqua: elsewhere on Tk 8.6 a notch is already 120,
    which the normalized path above covers.
    """
    if app._tk_root.tk.call("tk", "windowingsystem") != "aqua":
        pytest.skip("legacy delta of 1 is Aqua-only")
    assert wheel.wheel_notches(app._tk_root, _FakeEvent(delta=delta)) == expected


@pytest.mark.parametrize("num, expected", [(4, 1.0), (5, -1.0), (6, 1.0), (7, -1.0)])
def test_wheel_notches_handles_x11_buttons(app, num, expected):
    """Legacy X11 wheel buttons still resolve to a signed notch count."""
    assert wheel.wheel_notches(app._tk_root, _FakeEvent(num=num)) == expected


def test_wheel_notches_survives_a_missing_delta(app):
    """A malformed event yields no scroll rather than raising."""
    assert wheel.wheel_notches(app._tk_root, _FakeEvent(delta="")) == 0.0


# --- precise delta unpacking ---------------------------------------------


@pytest.mark.parametrize(
    "packed, expected",
    [
        (30, (0, 30)),
        ((2 << 16) | 36, (2, 36)),
        (0xFFFF, (0, -1)),          # dy = -1
        ((1 << 16) | 17, (1, 17)),
        (0, (0, 0)),
    ],
)
def test_precise_deltas_unpacks_both_axes(packed, expected):
    """`%D` carries dx in the high 16 bits and signed dy in the low 16."""
    assert wheel.precise_deltas(_FakeEvent(delta=packed)) == expected


# --- pixel accumulator ----------------------------------------------------


def test_accumulator_carries_the_remainder():
    """Sub-step deltas add up instead of being dropped."""
    acc = wheel.PixelAccumulator()
    assert acc.add(0, 10, 1, 32) == (0, 0)
    assert acc.add(0, 10, 1, 32) == (0, 0)
    assert acc.add(0, 15, 1, 32) == (0, 1)  # 35 >= 32, 3px carried
    assert acc.add(0, 29, 1, 32) == (0, 1)  # 3 + 29 == 32


def test_accumulator_handles_a_zero_step():
    """A widget reporting no row height still scrolls rather than dividing by zero."""
    acc = wheel.PixelAccumulator()
    assert acc.add(0, 5, 0, 0) == (0, 5)


# --- integration: the widgets that were dead on Tk 9 ----------------------


@requires_touchpad
def test_scrollview_scrolls_on_touchpad(shown_app):
    """A trackpad gesture moves a ScrollView. Fails pre-fix (no binding)."""
    with bs.ScrollView(height=100) as sv:
        for i in range(60):
            bs.Label(f"row {i}")
    shown_app._tk_root.update()

    start = sv._internal.canvas.yview()[0]
    for _ in range(40):
        sv._internal.canvas.event_generate("<TouchpadScroll>", delta=_packed(0, -40))
    shown_app._tk_root.update()

    assert sv._internal.canvas.yview()[0] > start


@requires_touchpad
def test_scrollview_scrolls_on_wheel(shown_app):
    """A wheel notch moves a ScrollView by one unit, not 120."""
    with bs.ScrollView(height=100) as sv:
        for i in range(60):
            bs.Label(f"row {i}")
    shown_app._tk_root.update()

    sv._internal.canvas.event_generate("<MouseWheel>", delta=-120)
    shown_app._tk_root.update()
    after_one = sv._internal.canvas.yview()[0]

    # One notch must not run the view to the very end.
    assert 0.0 < after_one < 1.0


@requires_touchpad
def test_listview_scrolls_on_touchpad(shown_app, monkeypatch):
    """A trackpad gesture advances a ListView's first visible row.

    The pointer-containment guard (which stops a gesture over a nested
    widget from scrolling the list underneath) cannot be simulated with a
    synthetic event, so only that check is stubbed.
    """
    lv = bs.ListView(items=[{"label": f"item {i}"} for i in range(200)], height=120)
    shown_app._tk_root.update()

    view = lv._internal
    monkeypatch.setattr(type(view), "_pointer_within", lambda self, event: True)

    assert view._datasource.count > view._visible_rows, "list must overflow to scroll"
    start = view._start_index
    for _ in range(20):
        view.event_generate("<TouchpadScroll>", delta=_packed(0, -40))
    shown_app._tk_root.update()

    assert view._start_index > start


@requires_touchpad
def test_textarea_scrolls_on_touchpad(shown_app):
    """A trackpad gesture scrolls a TextArea.

    Tk 9 binds `<TouchpadScroll>` on the `Text` class itself, so this
    passes even without our handler. It guards the end-to-end behavior,
    not the fix — the ScrollView and ListView cases cover the regression.
    """
    ta = bs.TextArea(value="\n".join(f"line {i}" for i in range(400)), height=5)
    shown_app._tk_root.update()

    text = ta._text_widget()
    start = text.yview()[0]
    for _ in range(20):
        text.event_generate("<TouchpadScroll>", delta=_packed(0, -40))
    shown_app._tk_root.update()

    assert text.yview()[0] > start


@requires_touchpad
def test_touchpad_binding_is_registered(shown_app):
    """Every scrolling widget binds the sequence, not just the wheel."""
    with bs.ScrollView(height=80) as sv:
        bs.Label("content")
    shown_app._tk_root.update()

    bound = sv._internal.bind_class(sv._internal._scroll_tag)
    assert "<TouchpadScroll>" in bound
