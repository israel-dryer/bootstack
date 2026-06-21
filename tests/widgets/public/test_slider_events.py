"""GUI tests for Slider / RangeSlider event payloads.

Sliders emit their ``<<Change>>`` / ``<<Commit>>`` virtual events on a plain
``tk.Frame``, which Tk only delivers to a **mapped** widget. These tests show
the window (``deiconify``) and pump the event loop so the events actually fire —
exercising the real path a running app uses — then assert the handler receives
the typed payload from ``bootstack.events`` (unpacked, not a raw event).
"""
from __future__ import annotations

import pytest

import bootstack as bs
from bootstack.events import (
    RangeSliderCommitEvent,
    RangeSliderEvent,
    SliderCommitEvent,
    SliderEvent,
)


def _pump(app) -> None:
    root = app._tk_root
    root.update_idletasks()
    root.update()


@pytest.mark.gui
def test_slider_on_change_delivers_slider_event(shown_app):
    received = []
    s = bs.Slider(value=0, min_value=0, max_value=100)
    s.on_change(received.append)
    _pump(shown_app)

    s.value = 42
    _pump(shown_app)

    assert len(received) == 1
    e = received[0]
    assert isinstance(e, SliderEvent)          # unpacked payload, not a raw Event
    assert e.value == 42.0
    assert e.prev_value == 0.0


@pytest.mark.gui
def test_slider_on_commit_delivers_commit_event(shown_app):
    received = []
    s = bs.Slider(value=10, min_value=0, max_value=100)
    s.on_commit(received.append)
    _pump(shown_app)

    # Commit fires on drag-release / keyboard step; emit it directly here.
    s._internal.event_generate("<<Commit>>", data=SliderCommitEvent(value=10.0))
    _pump(shown_app)

    assert len(received) == 1
    e = received[0]
    assert isinstance(e, SliderCommitEvent)
    assert e.value == 10.0


@pytest.mark.gui
def test_slider_change_stream_unpacks_payload(shown_app):
    """The Stream form delivers the same unpacked payload to operators."""
    values = []
    s = bs.Slider(value=0, min_value=0, max_value=100)
    s.on_change().map(lambda e: e.value).listen(values.append)
    _pump(shown_app)

    s.value = 25
    _pump(shown_app)

    assert values == [25.0]


@pytest.mark.gui
def test_rangeslider_on_change_delivers_range_event(shown_app):
    received = []
    rs = bs.RangeSlider(low_value=10, high_value=90, min_value=0, max_value=100)
    rs.on_change(received.append)
    _pump(shown_app)

    rs.low_value = 20
    _pump(shown_app)

    assert received, "on_change did not fire"
    e = received[-1]
    assert isinstance(e, RangeSliderEvent)
    assert e.low_value == 20.0
    assert e.high_value == 90.0


@pytest.mark.gui
def test_rangeslider_on_commit_delivers_range_commit_event(shown_app):
    received = []
    rs = bs.RangeSlider(low_value=10, high_value=90, min_value=0, max_value=100)
    rs.on_commit(received.append)
    _pump(shown_app)

    rs._internal.event_generate(
        "<<Commit>>", data=RangeSliderCommitEvent(low_value=10.0, high_value=90.0)
    )
    _pump(shown_app)

    assert len(received) == 1
    e = received[0]
    assert isinstance(e, RangeSliderCommitEvent)
    assert e.low_value == 10.0
    assert e.high_value == 90.0
