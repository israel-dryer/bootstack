"""A `Signal` can represent an empty value when it declares one (#390).

`Signal` is strictly monomorphic — the type comes from the seed and `set(None)`
raised unconditionally — so a field bound to a signal could never report being
cleared. It silently kept its last value. `nullable=True` declares that a signal
can hold nothing, and the field family pushes an empty value through only for
signals that say so.
"""
from datetime import date, time

import pytest

import bootstack as bs
from bootstack.errors import BootstackError


# --------------------------------------------------------------------------
# The Signal itself
# --------------------------------------------------------------------------

def test_a_nullable_signal_accepts_none(app):
    """The headline: an empty value is storable and reaches subscribers."""
    sig = bs.Signal(date(2024, 5, 5), nullable=True)
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    sig.set(None)

    assert sig() is None
    assert seen == [None]


def test_a_non_nullable_signal_still_rejects_none(app):
    """The control for the test above — the guard is untouched by default."""
    sig = bs.Signal(date(2024, 5, 5))

    with pytest.raises(TypeError, match="got NoneType"):
        sig.set(None)

    assert sig() == date(2024, 5, 5)


def test_nullable_is_readable_and_defaults_off(app):
    assert bs.Signal(1, nullable=True).nullable is True
    assert bs.Signal(1).nullable is False


def test_a_nullable_signal_seeded_empty_locks_its_type_on_the_first_value(app):
    """Deferred inference, not abandoned inference.

    `bs.Signal(None, nullable=True)` is the spelling a caller reaches for when
    the value starts empty. It has no type to infer, so the first real value
    decides it — and the signal is monomorphic from then on, exactly as one
    seeded with a value would be.
    """
    sig = bs.Signal(None, nullable=True)
    assert sig.type is None
    assert sig() is None

    sig.set(date(2024, 1, 2))
    assert sig.type is date

    with pytest.raises(TypeError, match="Expected date, got int"):
        sig.set(5)

    # And it can go back to empty afterwards.
    sig.set(None)
    assert sig() is None


def test_the_rejection_message_names_the_way_out(app):
    """A caller who hits the guard should not have to search for `nullable`."""
    with pytest.raises(TypeError, match="nullable=True"):
        bs.Signal(1).set(None)


def test_a_none_typed_signal_still_no_ops_on_none(app):
    """A signal whose type IS NoneType keeps taking `None`, as it did on 0.3.2.

    `map()` produces one whenever the transform returns `None` for the value it
    is first called with, so this shape reaches code that has no nullable signal
    anywhere in it. The write is a no-op either way — but the guard raises out of
    the *source's* `set()`, through the subscriber fan-out, which is a Tk trace
    once the source is realized.
    """
    src = bs.Signal(0)
    derived = src.map(lambda v: None)
    assert derived.type is type(None)

    src.set(1)

    assert derived() is None
    bs.Signal(None).set(None)  # the direct spelling, same rule


# --------------------------------------------------------------------------
# Bound to a field — the reported behavior
# --------------------------------------------------------------------------

def test_clearing_a_bound_field_reaches_a_nullable_signal(app):
    """The bug as reported: a cleared field left its signal holding stale data."""
    sig = bs.Signal(date(2024, 5, 5), nullable=True)
    field = bs.DateField(signal=sig, parent=app)
    app.tk.update()
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    field.value = None
    app.tk.update()

    assert field.value is None
    assert sig() is None
    assert seen == [None]


def test_an_empty_nullable_signal_clears_the_field_it_is_bound_to(app):
    """The other direction — writing None to the signal empties the field."""
    sig = bs.Signal(date(2024, 5, 5), nullable=True)
    field = bs.DateField(signal=sig, parent=app)
    app.tk.update()

    sig.set(None)
    app.tk.update()
    assert field.value is None

    sig.set(date(2025, 3, 3))
    app.tk.update()
    assert field.value == date(2025, 3, 3)


def test_clearing_a_bound_field_still_skips_a_non_nullable_signal(app):
    """Decision 3, pinned: the default is unchanged from 0.3.2.

    A non-nullable signal has no way to mean "cleared", so the write is skipped
    and the signal keeps its last value. That is deliberate, not an oversight —
    this test exists so a later change cannot quietly widen it.
    """
    sig = bs.Signal(date(2024, 5, 5))
    field = bs.DateField(signal=sig, parent=app)
    app.tk.update()

    field.value = None
    app.tk.update()

    assert field.value is None
    assert sig() == date(2024, 5, 5)


_OPTIONS = [("One", "1"), ("Two", "2")]


@pytest.mark.parametrize(
    "name, build, seed",
    [
        ("NumberField", lambda s, p: bs.NumberField(signal=s, parent=p), 5),
        ("DateField", lambda s, p: bs.DateField(signal=s, parent=p), date(2024, 5, 5)),
        ("TimeField", lambda s, p: bs.TimeField(signal=s, parent=p), time(9, 30)),
        ("Select", lambda s, p: bs.Select(options=_OPTIONS, signal=s, parent=p), "1"),
        ("SelectButton",
         lambda s, p: bs.SelectButton(options=_OPTIONS, signal=s, parent=p), "1"),
    ],
)
def test_the_value_space_fields_all_report_a_clear(app, name, build, seed):
    """Every field that binds a typed value, not display text.

    `Select` and `SelectButton` are why #390 landed on this milestone at all —
    #458 and #461 moved them off a `StringVar` that could carry `''`, which
    turned the family limitation into a regression for those two.
    """
    sig = bs.Signal(seed, nullable=True)
    field = build(sig, app)
    app.tk.update()

    field.value = None
    app.tk.update()

    assert sig() is None


def test_a_form_clear_reaches_nullable_signals(app):
    """The reporter's actual shape — `form.set({key: None})`."""
    sig = bs.Signal(date(2024, 5, 5), nullable=True)
    form = bs.Form(
        items=[bs.FieldItem(key="when", label="When", editor="datefield",
                            editor_options={"signal": sig})],
        parent=app,
    )
    app.tk.update()
    assert sig() == date(2024, 5, 5)

    form.set({"when": None})
    app.tk.update()

    assert form.get() == {"when": None}
    assert sig() is None


# --------------------------------------------------------------------------
# The boundary: a widget that stores the value itself cannot carry an empty one
# --------------------------------------------------------------------------

def test_binding_a_nullable_signal_to_a_text_field_raises(app):
    """A realized signal hands its variable to the widget, and Tk cannot hold None.

    Measured in plain tkinter: `IntVar.set(None)` and `DoubleVar.set(None)` do
    not raise — they store the literal `'None'` and fail at an arbitrary later
    read — while `StringVar` displays `'None'` to the user. So the binding is
    refused at the point it is made rather than corrupting quietly.
    """
    with pytest.raises(BootstackError, match="nullable Signal cannot be bound"):
        bs.TextField(textsignal=bs.Signal("hi", nullable=True), parent=app)


def test_binding_a_nullable_signal_to_a_checkbox_raises(app):
    with pytest.raises(BootstackError, match="nullable Signal cannot be bound"):
        bs.Checkbox("Agree", signal=bs.Signal(False, nullable=True), parent=app)


def test_the_refusal_message_says_what_to_do_instead(app):
    with pytest.raises(BootstackError, match="drop nullable=True"):
        bs.TextField(textsignal=bs.Signal("hi", nullable=True), parent=app)


def test_an_ordinary_signal_binds_to_those_widgets_as_before(app):
    """The control: the refusal is about `nullable`, not about the binding."""
    field = bs.TextField(textsignal=bs.Signal("hi"), parent=app)
    box = bs.Checkbox("Agree", signal=bs.Signal(False), parent=app)
    app.tk.update()

    assert field.value == "hi"
    assert box.value is False
