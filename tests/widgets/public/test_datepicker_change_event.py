"""Regression tests for the date picker emitting a change event (#388).

Choosing a date from the calendar applied the value but emitted no
`<<Change>>`, because the picker assigns `value` directly and that event is
only produced by the entry's change detection on FocusOut/Return. Every
consumer missed the selection: `on_change` handlers, a bound `Signal` (which
`ValueSignalMixin` syncs off `on_change`), and `Form` change tracking.

Range mode was already correct — `_set_range` emits its own event — so only
single-selection mode was affected.

These drive `_apply_picked`, the seam both picker call sites in
`_show_date_picker` funnel through, since the dialog itself needs a user
gesture. `development/verify_388_datepicker.py` covers the real click-through.

Filed from discussion #386.
"""
from __future__ import annotations

from datetime import date, datetime

import bootstack as bs


# --- The reported bug: a bound signal went stale ------------------------

def test_picking_a_date_updates_a_bound_signal(app):
    # Reported repro: after choosing a date in the picker, the signal still
    # reported the previously set value.
    signal = bs.Signal(date(2020, 1, 1))
    field = bs.DateField(signal=signal)
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2026, 7, 29))
    app._tk_root.update_idletasks()

    assert field.value == date(2026, 7, 29)
    assert signal() == date(2026, 7, 29)


def test_picking_a_date_fires_on_change(app):
    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2026, 7, 29))
    app._tk_root.update_idletasks()

    assert seen == [date(2026, 7, 29)]


def test_change_payload_carries_the_previous_value(app):
    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append((e.prev_value, e.value)))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2026, 7, 29))
    app._tk_root.update_idletasks()

    assert seen == [(date(2024, 1, 1), date(2026, 7, 29))]


# --- No duplicate events ------------------------------------------------

def test_applying_the_same_pick_twice_fires_once(app):
    # `_show_date_picker` applies the result from the dialog callback and again
    # from the post-show fallback, so the second application must be inert.
    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2026, 7, 29))
    field._internal._apply_picked(date(2026, 7, 29))
    app._tk_root.update_idletasks()

    assert seen == [date(2026, 7, 29)]


def test_picking_the_current_value_fires_nothing(app):
    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2024, 1, 1))
    app._tk_root.update_idletasks()

    assert seen == []


def test_a_later_focus_out_does_not_repeat_the_event(app):
    # The entry's last-seen value must advance with the pick, or blurring the
    # field afterwards would announce the same selection a second time.
    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(date(2026, 7, 29))
    field._entry_widget().event_generate("<FocusOut>")
    app._tk_root.update_idletasks()

    assert seen == [date(2026, 7, 29)]


# --- Value normalization ------------------------------------------------

def test_a_datetime_result_is_stored_as_a_date(app):
    field = bs.DateField(value=date(2024, 1, 1))
    app._tk_root.update_idletasks()

    field._internal._apply_picked(datetime(2026, 7, 29, 13, 45))

    assert field.value == date(2026, 7, 29)


# --- Range mode keeps its own emit --------------------------------------

def test_range_mode_fires_exactly_once(app):
    seen = []
    field = bs.DateField(selection_mode="range")
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._apply_picked((date(2026, 1, 1), date(2026, 1, 31)))
    app._tk_root.update_idletasks()

    assert seen == [(date(2026, 1, 1), date(2026, 1, 31))]


# --- The real picker path -----------------------------------------------

def test_show_date_picker_emits_the_change(app, monkeypatch):
    """Drive `_show_date_picker` itself, with the dialog stubbed out.

    The tests above exercise `_apply_picked` directly, so they would still
    pass if the picker stopped calling it. This one runs the actual method —
    both the dialog-result callback and the post-show fallback — and so fails
    if either call site regresses to a plain `value` assignment.
    """
    import bootstack.dialogs._impl.datedialog as datedialog_mod

    picked = date(2026, 7, 29)

    class _StubDateDialog:
        def __init__(self, **kwargs):
            self.result = picked
            self._handler = None

        def on_result(self, handler):
            self._handler = handler

        def show(self, **kwargs):
            if self._handler is not None:
                self._handler({"result": self.result})

    monkeypatch.setattr(datedialog_mod, "DateDialog", _StubDateDialog)

    seen = []
    field = bs.DateField(value=date(2024, 1, 1))
    field.on_change(lambda e: seen.append(e.value))
    app._tk_root.update_idletasks()

    field._internal._show_date_picker()
    app._tk_root.update_idletasks()

    assert field.value == picked
    # Exactly once, despite the callback and the fallback both applying it.
    assert seen == [picked]


# --- Form change tracking sees it ---------------------------------------

def test_form_data_reflects_a_picked_date(app):
    form = bs.Form(items=[
        bs.FieldItem(key="d", label="D", editor="datefield",
                     editor_options={"value": date(2024, 1, 1)}),
    ])
    app._tk_root.update_idletasks()

    form.field("d")._internal._apply_picked(date(2026, 7, 29))
    app._tk_root.update_idletasks()

    assert form.get()["d"] == date(2026, 7, 29)
