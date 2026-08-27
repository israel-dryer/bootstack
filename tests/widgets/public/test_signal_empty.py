"""A `Signal` can represent an empty value when it declares one (#390).

`Signal` is strictly monomorphic — the type comes from the seed and `set(None)`
raised unconditionally — so a field bound to a signal could never report being
cleared. It silently kept its last value. `allow_empty=True` declares that a
signal can be empty, and `clear()` is the verb, matching the `clear()` that ships
on nine field widgets.

The empty is decided by the binding, not by the type. A signal empties to `None`,
except where its value *is* a widget's Tk variable — a variable holds only
strings, so there it empties to `''`. Three types have no empty member at all —
`bool`, `int` and `float` — and a signal that allows empty refuses to back a
widget whose variable is one of them.
"""
from datetime import date, time

import pytest

import bootstack as bs
from bootstack.errors import BootstackError


# --------------------------------------------------------------------------
# The Signal itself
# --------------------------------------------------------------------------

def test_a_signal_that_allows_empty_accepts_none(app):
    """The headline: an empty value is storable and reaches subscribers."""
    sig = bs.Signal(date(2024, 5, 5), allow_empty=True)
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    sig.set(None)

    assert sig() is None
    assert seen == [None]


def test_a_signal_that_does_not_allow_empty_still_rejects_none(app):
    """The control for the test above — the guard is untouched by default."""
    sig = bs.Signal(date(2024, 5, 5))

    with pytest.raises(TypeError, match="got NoneType"):
        sig.set(None)

    assert sig() == date(2024, 5, 5)


def test_allows_empty_is_readable_and_defaults_off(app):
    assert bs.Signal(1, allow_empty=True).allows_empty is True
    assert bs.Signal(1).allows_empty is False


def test_the_rejection_message_names_the_way_out(app):
    """A caller who hits the guard should not have to search for the keyword."""
    with pytest.raises(TypeError, match="allow_empty=True"):
        bs.Signal(1).set(None)


def test_a_signal_seeded_empty_locks_its_type_on_the_first_value(app):
    """Deferred inference, not abandoned inference.

    `bs.Signal(None, allow_empty=True)` is the spelling a caller reaches for when
    the value starts empty. It has no type to infer, so the first real value
    decides it — and the signal is monomorphic from then on, exactly as one
    seeded with a value would be.
    """
    sig = bs.Signal(None, allow_empty=True)
    assert sig.type is None
    assert sig() is None

    sig.set(date(2024, 1, 2))
    assert sig.type is date

    with pytest.raises(TypeError, match="Expected date, got int"):
        sig.set(5)

    # And it can go back to empty afterwards.
    sig.set(None)
    assert sig() is None


def test_a_none_typed_signal_still_no_ops_on_none(app):
    """A signal whose type IS NoneType keeps taking `None`, as it did on 0.3.2.

    `map()` produces one whenever the transform returns `None` for the value it
    is first called with, so this shape reaches code with no empty-able signal
    anywhere in it. The write is a no-op either way — but the guard raises out of
    the *source's* `set()`, through the subscriber fan-out, which is a Tk trace
    once the source is realized.

    This pins the baseline rather than the fix: it passes against `main`'s
    `signal.py` too.
    """
    src = bs.Signal(0)
    derived = src.map(lambda v: None)
    assert derived.type is type(None)

    src.set(1)

    assert derived() is None
    bs.Signal(None).set(None)  # the direct spelling, same rule


# --------------------------------------------------------------------------
# clear() — one verb, a type-dependent empty
# --------------------------------------------------------------------------

def test_clear_empties_a_typed_signal_to_none(app):
    sig = bs.Signal(date(2024, 5, 5), allow_empty=True)
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    sig.clear()

    assert sig() is None
    assert seen == [None]


def test_clear_empties_a_bound_text_signal_to_the_empty_string(app):
    """The binding decides the empty, not the type — and this is the case that
    forces `''`: the value *is* the widget's variable, which holds only strings.

    This is the whole reason the parameter is spelled `allow_empty` rather than
    `nullable`: asked to be empty, this signal gives back `''`, which is what it
    promised. "Nullable" would have promised `None` and been unable to deliver.
    """
    sig = bs.Signal("hello", allow_empty=True)
    bs.TextField(textsignal=sig, parent=app)
    app.tk.update()
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    sig.clear()

    assert sig() == ""
    assert seen == [""]


def test_the_same_signal_type_empties_to_none_when_it_is_not_the_widgets_variable(app):
    """The control for the test above, and the principle in one pair.

    Both signals are `str`-typed. The text field's *is* the widget's variable, so
    its empty is `''`; a `Select`'s is synced in pure Python, so its empty is
    `None` — which is what the widget and its change event report for a cleared
    selection, and therefore what the signal has to agree with.
    """
    sig = bs.Signal("1", allow_empty=True)
    select = bs.Select(options=_OPTIONS, signal=sig, parent=app)
    app.tk.update()

    sig.clear()
    app.tk.update()

    assert sig() is None
    assert select.value is None


def test_set_none_normalizes_to_the_signals_empty(app):
    """So `form.set({key: None})` reads the same across a mixed form."""
    typed = bs.Signal(date(2024, 5, 5), allow_empty=True)
    typed.set(None)
    assert typed() is None

    text = bs.Signal("hello", allow_empty=True)
    bs.TextField(textsignal=text, parent=app)
    app.tk.update()
    text.set(None)
    assert text() == ""


def test_clear_still_needs_the_declaration(app):
    """`clear()` is not a way around the guard — it is a way to reach it.

    One rule, whatever the type: a signal empties only if it was declared able
    to. The message points at the keyword either way.
    """
    with pytest.raises(TypeError, match="allow_empty=True"):
        bs.Signal("hello").clear()

    with pytest.raises(TypeError, match="allow_empty=True"):
        bs.Signal(date(2024, 5, 5)).clear()


# --------------------------------------------------------------------------
# Bound to a field that carries a typed value — the reported behavior
# --------------------------------------------------------------------------

def test_clearing_a_bound_field_reaches_the_signal(app):
    """The bug as reported: a cleared field left its signal holding stale data."""
    sig = bs.Signal(date(2024, 5, 5), allow_empty=True)
    field = bs.DateField(signal=sig, parent=app)
    app.tk.update()
    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    field.value = None
    app.tk.update()

    assert field.value is None
    assert sig() is None
    assert seen == [None]


def test_an_empty_signal_clears_the_field_it_is_bound_to(app):
    """The other direction — emptying the signal empties the field."""
    sig = bs.Signal(date(2024, 5, 5), allow_empty=True)
    field = bs.DateField(signal=sig, parent=app)
    app.tk.update()

    sig.clear()
    app.tk.update()
    assert field.value is None

    sig.set(date(2025, 3, 3))
    app.tk.update()
    assert field.value == date(2025, 3, 3)


def test_clearing_a_bound_field_still_skips_a_signal_that_cannot_be_empty(app):
    """Decision 3, pinned: the default is unchanged from 0.3.2.

    A signal that does not allow empty has no way to mean "cleared", so the write
    is skipped and the signal keeps its last value. That is deliberate, not an
    oversight — this test exists so a later change cannot quietly widen it.
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

    Note `Select` and `SelectButton` seed with a `str` option key and still empty
    to `None`, not `''`: their signal is never realized, so the value is a Python
    option key rather than the contents of a variable. That is the binding
    deciding the empty, not the type.
    """
    sig = bs.Signal(seed, allow_empty=True)
    field = build(sig, app)
    app.tk.update()

    field.value = None
    app.tk.update()

    assert sig() is None


def test_a_form_clear_reaches_the_signal(app):
    """The reporter's actual shape — `form.set({key: None})`."""
    sig = bs.Signal(date(2024, 5, 5), allow_empty=True)
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
# Bound to a widget that stores the value in the signal's own variable
# --------------------------------------------------------------------------

def _var_contents(app, sig) -> str:
    """What Tcl actually holds — which is what a bound widget displays."""
    return app.tk.getvar(str(sig.var))


def test_an_empty_text_signal_clears_the_widget_it_backs(app):
    """The widening: a `StringVar` holds `''` natively, so the binding is allowed.

    Asserted on the entry rather than on `field.value`, which reports the last
    *committed* value and lags any programmatic signal write — pre-existing, and
    unrelated to emptiness (it lags a non-empty write identically).
    """
    sig = bs.Signal("hello", allow_empty=True)
    field = bs.TextField(textsignal=sig, parent=app)
    app.tk.update()
    entry = field._entry_widget()
    assert entry.get() == "hello"

    sig.clear()
    app.tk.update()

    assert entry.get() == ""
    assert sig() == ""


def test_an_empty_text_signal_renders_blank_not_the_word_none(app):
    """The corruption test, and the reason `''` is written rather than `str(None)`.

    A bare `None` handed to Tk stringifies to the four characters `None`, which
    the widget then displays. Asserted on the variable's contents because that is
    the thing a user would see.
    """
    sig = bs.Signal(None, allow_empty=True)
    bs.Label(textsignal=sig, parent=app)
    app.tk.update()

    assert _var_contents(app, sig) == ""

    sig.set("something")
    sig.set(None)
    app.tk.update()

    assert _var_contents(app, sig) == ""


def test_clearing_a_radiogroup_signal_selects_nothing(app):
    """`RadioGroup`/`ToggleGroup` were the near-miss shelved onto #369.

    They come in for free under the empty framing: unselected already *is* `''`
    for them, so the empty they need is the one their variable already has.
    """
    sig = bs.Signal("a", allow_empty=True)
    group = bs.RadioGroup(options=[("a", "Apple"), ("b", "Banana")], signal=sig,
                          parent=app)
    app.tk.update()
    assert group.value == "a"

    sig.clear()
    app.tk.update()

    assert group.value == ""
    assert sig() == ""


# --------------------------------------------------------------------------
# The floor: three types have no empty member, on any Tk version
# --------------------------------------------------------------------------

def test_binding_an_empty_signal_to_a_checkbox_raises(app):
    """`BooleanVar` refuses both `''` and `None` at the write.

    A tristate `Checkbox` does have a third state — but it holds that state in
    the widget, not in the variable, which reads the same for indeterminate and
    for off (measured: `'0'` either way). So the empty a checkbox has is not one
    the variable can carry, and the binding is refused where it is made rather
    than reporting an indeterminate checkbox as an unchecked one.
    """
    with pytest.raises(BootstackError, match="no way to hold an empty value"):
        bs.Checkbox("Agree", signal=bs.Signal(False, allow_empty=True), parent=app)


def test_binding_an_empty_signal_to_a_slider_raises(app):
    """`DoubleVar` is the dangerous one: it accepts and fails later, invisibly.

    Measured in plain tkinter — `DoubleVar.set(None)` does not raise, it stores
    the literal `'None'` and detonates at an arbitrary later `get()`, inside a Tk
    trace where nothing Python can see it.
    """
    with pytest.raises(BootstackError, match="no way to hold an empty value"):
        bs.Slider(signal=bs.Signal(0.0, allow_empty=True), parent=app)


def test_the_refusal_message_names_the_variable_that_cannot_hold_an_empty(app):
    with pytest.raises(BootstackError, match="own bool variable"):
        bs.Checkbox("Agree", signal=bs.Signal(False, allow_empty=True), parent=app)


def test_an_ordinary_signal_binds_to_those_widgets_as_before(app):
    """The control: the refusal is about the declaration, not about the binding."""
    box = bs.Checkbox("Agree", signal=bs.Signal(False), parent=app)
    slider = bs.Slider(signal=bs.Signal(0.0), parent=app)
    app.tk.update()

    assert box.value is False
    assert slider.value == 0.0
