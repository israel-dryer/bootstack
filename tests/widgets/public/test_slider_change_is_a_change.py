"""A slider `<<Change>>` reports a move that happened (#509).

`SliderEvent.prev_value` is documented as *"The value before this move."* It was
not: a drag across a `step=10` slider produced 574 events of which **564 carried
`prev_value == value`**. `_var.set()` writes on every pixel, a Tk write trace
fires on every write even when the value is unchanged, and `_snap()` collapses
every pixel inside a step onto the same number — so most of the traffic reported
a move from a value to itself.

`_impl/composites/meter.py:430-438` already guarded the identical emit. This is
that pattern applied to the two widgets that skipped it.

⚠ SLIDERS ARE LIVE BY DESIGN AND STAY LIVE. Nothing here is deferred, debounced
or held: the event fires the instant the value crosses onto the next step,
mid-drag. `SliderEvent` ("while a slider value moves") and `SliderCommitEvent`
are separate payload types precisely so the live/committed split is typed, and
`on_commit` is untouched.

⚠ THE NO-STEP ARM IS THE CONTROL AND IT IS WHAT MAKES THIS FILE MEAN ANYTHING.
The stepped assertions below pass just as well for a build that stopped emitting
during a drag entirely — that is the shape a too-eager guard would take. Only a
continuous slider still emitting hundreds of events over the same sweep separates
"suppressed the redundant ones" from "broke live updates".

⚠ Marked `gui` on `shown_app`: sliders emit on a plain `tk.Frame`, which Tk only
delivers to a MAPPED widget — see the header of `test_slider_events.py`. Each
sweep asserts the canvas is mapped and has real width first, so a sweep that
never reached the widget cannot read as "no redundant events".
"""
from __future__ import annotations

import pytest

import bootstack as bs


TRACK_WIDTH = 420
MIN_TRACK_WIDTH = 200


def _pump(app, times: int = 3) -> None:
    root = app._tk_root
    for _ in range(times):
        root.update_idletasks()
        root.update()


def _wide(factory):
    """Build a slider inside a sized container so its track has real width.

    A slider takes no `width=`; it fills its parent. Dropped straight into the
    shared root's content region its canvas comes up **1px wide**, and a sweep
    across one pixel produces no events at all — which every assertion in this
    file would read as success. Measured, not assumed: bare slider 1px, the same
    slider inside `Column(width=420, horizontal_items="stretch")` 420px.
    """
    with bs.Column(width=TRACK_WIDTH, height=60, horizontal_items="stretch"):
        return factory()


def _canvas(app, widget):
    """The slider's track canvas, proven usable before any sweep runs.

    A geometry assertion on an unmapped or zero-width canvas passes vacuously —
    no motion event reaches the widget, so no event is redundant and the test
    reports success for a sweep that never happened.
    """
    cv = widget._internal._canvas
    _pump(app, 5)
    assert cv.winfo_ismapped(), "the slider canvas is not mapped; the sweep would reach nothing"
    assert cv.winfo_width() >= MIN_TRACK_WIDTH, (
        "the track is %dpx wide, too narrow to sweep meaningfully"
        % cv.winfo_width()
    )
    return cv


def _sweep(app, widget, sink: list, start_frac: float = 0.0, end_frac: float = 1.0) -> list:
    """Press, drag one pixel at a time between two fractions of the track, release.

    Returns the events recorded during the drag. The press happens BEFORE the
    sink is cleared, so the event it produces is not counted as part of the
    sweep.
    """
    cv = _canvas(app, widget)
    width = cv.winfo_width()
    ymid = cv.winfo_height() // 2
    lo_x = max(5, int(width * start_frac))
    hi_x = min(width - 5, int(width * end_frac))
    step = 1 if hi_x >= lo_x else -1

    cv.event_generate("<Button-1>", x=lo_x, y=ymid)
    _pump(app)
    sink.clear()

    for px in range(lo_x, hi_x + step, step):
        cv.event_generate("<B1-Motion>", x=px, y=ymid)
    cv.event_generate("<ButtonRelease-1>", x=hi_x, y=ymid)
    _pump(app)
    return list(sink)


# ---------------------------------------------------------------------------
# Slider
# ---------------------------------------------------------------------------

@pytest.mark.gui
def test_a_stepped_drag_reports_no_move_from_a_value_to_itself(shown_app):
    """The headline: every event carries two different values."""
    received: list = []
    s = _wide(lambda: bs.Slider(value=0, min_value=0, max_value=100, step=10))
    s.on_change(received.append)
    _pump(shown_app)

    events = _sweep(shown_app, s, received)

    assert events, "the sweep produced no events at all"
    redundant = [e for e in events if e.value == e.prev_value]
    assert redundant == [], (
        "%d of %d events reported a move from a value to itself"
        % (len(redundant), len(events))
    )


@pytest.mark.gui
def test_a_stepped_drag_emits_once_per_step_it_crosses(shown_app):
    """One event per distinct value — the count follows the steps, not the pixels.

    Before the guard the same sweep emitted one event per pixel of travel, so
    the count tracked the width of the widget rather than the values it visited.
    """
    received: list = []
    s = _wide(lambda: bs.Slider(value=0, min_value=0, max_value=100, step=10))
    s.on_change(received.append)
    _pump(shown_app)

    events = _sweep(shown_app, s, received)
    distinct = {round(e.value, 6) for e in events}

    assert len(events) == len(distinct), (
        "%d events carried only %d distinct values"
        % (len(events), len(distinct))
    )


@pytest.mark.gui
def test_a_continuous_drag_still_reports_every_pixel_of_travel(shown_app):
    """THE CONTROL. A slider with no step is live and must stay live.

    Without this arm, a guard that suppressed everything — or a drag that never
    reached the widget — would satisfy the two tests above.
    """
    received: list = []
    s = _wide(lambda: bs.Slider(value=0, min_value=0, max_value=100))
    s.on_change(received.append)
    _pump(shown_app)

    events = _sweep(shown_app, s, received)

    assert len(events) > 100, (
        "a continuous drag emitted only %d events; live updating is broken"
        % len(events)
    )
    redundant = [e for e in events if e.value == e.prev_value]
    assert redundant == [], (
        "%d of %d continuous events reported a move from a value to itself"
        % (len(redundant), len(events))
    )


# ---------------------------------------------------------------------------
# RangeSlider — driven on the HIGH handle
# ---------------------------------------------------------------------------
#
# `_on_canvas_click` assigns the drag to whichever handle is nearer the press
# (`rangeslider.py:621`), so pressing at the right edge of a full-width range
# picks "hi" and the sweep runs through `_on_hi_write`. That is the guard most
# easily left out — it is a second copy of `_on_lo_write` in the same file.


def _range_redundant(events: list) -> list:
    """Events where NEITHER end moved. The payload carries both, so both decide."""
    return [
        e for e in events
        if e.low_value == e.prev_low_value and e.high_value == e.prev_high_value
    ]


@pytest.mark.gui
def test_a_stepped_range_drag_reports_no_move_from_a_value_to_itself(shown_app):
    received: list = []
    rs = _wide(lambda: bs.RangeSlider(
        low_value=0, high_value=100, min_value=0, max_value=100, step=10))
    rs.on_change(received.append)
    _pump(shown_app)

    events = _sweep(shown_app, rs, received, start_frac=1.0, end_frac=0.5)

    assert events, "the sweep produced no events at all"

    # Prove WHICH handle this drove, rather than trusting the press location to
    # keep picking it. `_on_lo_write` and `_on_hi_write` are near-identical
    # bodies, and the guard was landed on one of them first — if the
    # nearest-handle logic ever changes, this fails loudly instead of quietly
    # covering `_on_lo_write` twice and `_on_hi_write` not at all.
    assert {e.low_value for e in events} == {0.0}, (
        "the low end moved (%r); this sweep is not exercising _on_hi_write"
        % (sorted({e.low_value for e in events}),)
    )
    assert len({e.high_value for e in events}) > 1, "the high end never moved"

    redundant = _range_redundant(events)
    assert redundant == [], (
        "%d of %d events reported a move with neither end changing"
        % (len(redundant), len(events))
    )


@pytest.mark.gui
def test_a_continuous_range_drag_still_reports_every_pixel_of_travel(shown_app):
    """The same control, on the same handle."""
    received: list = []
    rs = _wide(lambda: bs.RangeSlider(
        low_value=0, high_value=100, min_value=0, max_value=100))
    rs.on_change(received.append)
    _pump(shown_app)

    events = _sweep(shown_app, rs, received, start_frac=1.0, end_frac=0.5)

    assert len(events) > 50, (
        "a continuous range drag emitted only %d events; live updating is broken"
        % len(events)
    )
    assert _range_redundant(events) == []