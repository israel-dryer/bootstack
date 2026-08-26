"""#459 — `TimeField(signal=…)` fired a change event while seeding at construction.

`ValueSignalMixin._bind_value_signal` seeds by assigning `self.value`.
`TimeField` is select-backed, and `SelectBox`'s value setter emits `<<Change>>`
on a programmatic set, so construction announced a selection the user never
made. `NumberField` and `DateField` share the mixin but not that internal, so
they stayed quiet — `TimeField` was the outlier among the three, and it
disagreed with its own `value=` door.

The emit is QUEUED (`when='tail'`), which is what makes it reach application
code: a handler bound on the line *after* the constructor still receives it
once the loop turns. An app reacting to a time change therefore fired that
reaction once at startup.

Measured on `main` before the fix:

    TimeField(signal=Signal(time(9, 0)))  -> [datetime.time(9, 0)]
    TimeField(value=time(9, 0))           -> []      <- same widget, no signal
    NumberField(signal=Signal(5))         -> []      <- sibling on the same mixin
    DateField(signal=Signal(date(...)))   -> []      <- sibling on the same mixin

Fixed the way #458 fixed it for `Select`: suppress the emit for the duration of
the seed only, so every later write still announces normally.
"""
import datetime

import bootstack as bs


def _seed_and_watch(app, widget):
    """Bind a handler AFTER construction, then turn the loop.

    The binding order is the point — it reproduces what an application does,
    and a queued seed emit is delivered to it.
    """
    seen: list = []
    widget.on_change(lambda e: seen.append(e.value))
    app.tk.update()
    return seen


def test_seeding_a_signal_does_not_fire_change(app):
    """The issue, verbatim."""
    field = bs.TimeField(signal=bs.Signal(datetime.time(9, 0)))

    assert _seed_and_watch(app, field) == []


def test_the_value_door_is_the_control(app):
    """`value=` seeds the same field and stays quiet.

    In-file rather than assumed: the two doors agreeing IS the argument that
    the signal door was the one that was wrong.
    """
    field = bs.TimeField(value=datetime.time(9, 0))

    assert _seed_and_watch(app, field) == []


def test_a_later_signal_write_still_fires_change(app):
    """The suppression must be seed-only.

    Guards the failure mode where silencing construction silences the field
    outright — which would pass the test above while breaking the widget.
    """
    signal = bs.Signal(datetime.time(9, 0))
    field = bs.TimeField(signal=signal)
    seen: list = []
    field.on_change(lambda e: seen.append(e.value))

    signal.set(datetime.time(14, 30))
    app.tk.update()

    assert seen == [datetime.time(14, 30)]
    assert field.value == datetime.time(14, 30)


def test_a_later_value_set_still_fires_change(app):
    """The same guard through the other door."""
    field = bs.TimeField(signal=bs.Signal(datetime.time(9, 0)))
    seen: list = []
    field.on_change(lambda e: seen.append(e.value))

    field.value = datetime.time(14, 30)
    app.tk.update()

    assert seen == [datetime.time(14, 30)]


def test_the_mixin_siblings_stay_quiet(app):
    """`NumberField` and `DateField` already passed; this guards the mixin edit.

    The fix is in `TimeField`, not in `ValueSignalMixin` — if a later change
    moves it into the mixin, these two are how you learn it over-reached.
    """
    number = bs.NumberField(signal=bs.Signal(5))
    date_field = bs.DateField(signal=bs.Signal(datetime.date(2026, 1, 1)))

    assert _seed_and_watch(app, number) == []
    assert _seed_and_watch(app, date_field) == []


def test_the_seeded_value_actually_landed(app):
    """The precondition every test above needs.

    Without it they pass vacuously on a build where seeding does nothing at
    all — no value written, so of course no change announced.
    """
    field = bs.TimeField(signal=bs.Signal(datetime.time(9, 0)))

    assert field.value == datetime.time(9, 0)
