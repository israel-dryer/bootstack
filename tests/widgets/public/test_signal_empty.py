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
from enum import IntEnum

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


def test_a_signal_that_starts_empty_declares_its_type(app):
    """`dtype=` names the type when there is no value to read one from.

    A signal that starts empty is still monomorphic from birth, exactly as one
    seeded with a value is — the type just arrives by declaration instead of by
    inference.
    """
    sig = bs.Signal(None, allow_empty=True, dtype=date)
    assert sig.type is date
    assert sig() is None

    sig.set(date(2024, 1, 2))
    assert sig() == date(2024, 1, 2)

    with pytest.raises(TypeError, match="Expected date, got int"):
        sig.set(5)

    # And it can go back to empty afterwards.
    sig.set(None)
    assert sig() is None


def test_starting_empty_without_a_declared_type_raises(app):
    """There is no deferred type: a signal never exists without knowing its own.

    Inferring from the first value written was measured to leave the signal
    typeless for as long as the caller left it empty — long enough to be bound
    to a widget, which is where it did damage (#390 round 2, findings 1 and 2).
    """
    with pytest.raises(TypeError, match="must declare one"):
        bs.Signal(None, allow_empty=True)


def test_a_declared_type_is_honored_alongside_a_value_seed(app):
    """The seed may be computed, so `dtype=` cannot be conditional on it.

    `bs.Signal(record.get('due'), allow_empty=True, dtype=date)` is the shape
    this exists for: whether the seed is a value or `None` is data, not a
    different spelling.
    """
    assert bs.Signal(date(2024, 1, 2), allow_empty=True, dtype=date).type is date
    assert bs.Signal(None, allow_empty=True, dtype=date).type is date


def test_a_seed_that_contradicts_the_declared_type_raises_at_construction(app):
    """Named rather than discarded — the write that fails later is not the bug."""
    with pytest.raises(TypeError, match="seeded with int but declares dtype=str"):
        bs.Signal(5, allow_empty=True, dtype=str)


def test_a_declared_float_widens_an_int_seed(app):
    """The seed passes exactly the test every later write passes, widening included."""
    sig = bs.Signal(0, allow_empty=True, dtype=float)
    assert sig.type is float
    assert sig() == 0.0


def test_dtype_takes_the_type_itself_not_its_name(app):
    """`Form`'s field spec accepts `'date'` too; a signal's does not, and says so."""
    with pytest.raises(TypeError, match="dtype must be a type"):
        bs.Signal(None, allow_empty=True, dtype="date")


def test_a_declared_type_still_needs_allow_empty_to_start_empty(app):
    """`dtype=` names a type; it does not also grant permission to be empty."""
    with pytest.raises(TypeError, match="needs allow_empty=True"):
        bs.Signal(None, dtype=date)


@pytest.mark.parametrize("dtype,expected_var", [
    (str, "StringVar"),
    (date, "StringVar"),
    (set, "SetVar"),
])
def test_a_signal_that_starts_empty_gets_the_variable_its_type_calls_for(
        app, dtype, expected_var):
    """The variable follows the declared type, not the seed (#390 round 2, finding 2).

    Dispatching on the seed made every signal that started empty a `StringVar`
    for life, so one that later held an `int` reported `type is int` while
    returning `'5'`, and `clear()` raised out of its own setter.
    """
    sig = bs.Signal(None, allow_empty=True, dtype=dtype)
    assert type(sig.var).__name__ == expected_var


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

    ⚠ The realized arm is the one that matters, and it is the one this test did
    not have. `clear()` used to pass `_empty_value()` to `set()`, which for a
    realized `str` signal is `''` — a valid `str`, so the `value is None` guard
    never ran and any text signal could be cleared undeclared. Both original
    arms are unrealized, so both passed while the rule they assert was false
    (#390 round 2, finding 3).
    """
    with pytest.raises(TypeError, match="allow_empty=True"):
        bs.Signal("hello").clear()

    with pytest.raises(TypeError, match="allow_empty=True"):
        bs.Signal(date(2024, 5, 5)).clear()

    realized = bs.Signal("hello")
    field = bs.TextField(textsignal=realized, parent=app)
    app.tk.update()
    assert realized._var is not None, "precondition: the binding realized it"

    with pytest.raises(TypeError, match="allow_empty=True"):
        realized.clear()

    assert realized() == "hello"
    assert field.value == "hello"


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
    sig = bs.Signal(None, allow_empty=True, dtype=str)
    bs.Label(textsignal=sig, parent=app)
    app.tk.update()

    assert _var_contents(app, sig) == ""

    sig.set("something")
    sig.set(None)
    app.tk.update()

    assert _var_contents(app, sig) == ""


def test_clearing_a_set_signal_gives_the_empty_set(app):
    """A `set` empties to `set()`, not to `''` — the one type answer here.

    `_empty_value()` returned `''` for any realized native-mode signal, and a
    `SetVar` refuses a `str` outright, so `clear()` on a multi-select's signal
    raised `Expected set or frozenset, got str` out of the caller. The empty set
    is a legal value of the type in both stores, so it needs no proxy at all
    (#390 round 2, finding 4).
    """
    sig = bs.Signal({"a"}, allow_empty=True)
    group = bs.ToggleGroup(options=["a", "b"], mode="multi", signal=sig, parent=app)
    app.tk.update()
    assert sig._var is not None, "precondition: the binding realized it"

    seen: list = []
    sig.subscribe(lambda v: seen.append(v))

    sig.clear()
    app.tk.update()

    assert sig() == set()
    assert group.value == set()
    assert seen == [set()]


def test_a_set_signal_empties_the_same_way_before_it_is_bound(app):
    """The control for the arm above: `set()` either way, unlike `str`.

    Where a `str` signal's empty legitimately depends on whether it backs a
    widget's variable, a `set`'s does not — so realization must not move it.
    """
    sig = bs.Signal({"a"}, allow_empty=True)
    assert sig._var is None, "precondition: nothing has realized it"

    sig.clear()

    assert sig() == set()


def test_a_subclass_of_a_native_type_keeps_its_variable(app):
    """An `IntEnum` is an `int`, and must land on the same variable one does.

    The seed-dispatching `_create_variable` this replaced asked `isinstance`,
    which catches subclasses. Asking `self._type is int` instead silently sent
    every `IntEnum` and `int` subclass to a `StringVar`, so `sig()` returned
    `'1'` where it had returned `1` and `sig() == Color.RED` went from True to
    False. Measured against `main`, which returns `1`.
    """
    class Color(IntEnum):
        RED = 1
        BLUE = 2

    sig = bs.Signal(Color.RED)
    assert type(sig.var).__name__ == "IntVar"
    assert sig() == 1
    assert sig() == Color.RED

    sig.set(Color.BLUE)
    assert sig() == Color.BLUE


def test_a_subclass_of_a_native_type_is_native_when_the_type_is_declared(app):
    """The declared path must answer the way the seeded one does.

    `_is_tk_native_type` had the same identity test as `_create_variable`, so a
    declared `IntEnum` was treated as an object-mode type while the same value
    seeded was treated as native.
    """
    class Color(IntEnum):
        RED = 1

    seeded = bs.Signal(Color.RED)
    declared = bs.Signal(None, allow_empty=True, dtype=Color)

    assert declared._object_mode == seeded._object_mode


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

# Both spellings of the same declaration reach the guard. Round 2's finding 1
# was that only the seeded one did: a signal that started empty had no type yet,
# so `self._type in (bool, int, float)` was False and the binding went through.
_EMPTY_BOOL = [
    pytest.param(lambda: bs.Signal(False, allow_empty=True), id="value-seeded"),
    pytest.param(lambda: bs.Signal(None, allow_empty=True, dtype=bool), id="starts-empty"),
]
_EMPTY_FLOAT = [
    pytest.param(lambda: bs.Signal(0.0, allow_empty=True), id="value-seeded"),
    pytest.param(lambda: bs.Signal(None, allow_empty=True, dtype=float), id="starts-empty"),
]


@pytest.mark.parametrize("make_signal", _EMPTY_BOOL)
def test_binding_an_empty_signal_to_a_checkbox_raises(app, make_signal):
    """`BooleanVar` refuses both `''` and `None` at the write.

    A tristate `Checkbox` does have a third state — but it holds that state in
    the widget, not in the variable, which reads the same for indeterminate and
    for off (measured: `'0'` either way). So the empty a checkbox has is not one
    the variable can carry, and the binding is refused where it is made rather
    than reporting an indeterminate checkbox as an unchecked one.
    """
    with pytest.raises(BootstackError, match="no way to hold an empty value"):
        bs.Checkbox("Agree", signal=make_signal(), parent=app)


@pytest.mark.parametrize("make_signal", _EMPTY_FLOAT)
def test_binding_an_empty_signal_to_a_slider_raises(app, make_signal):
    """`DoubleVar` is the dangerous one: it accepts and fails later, invisibly.

    Measured in plain tkinter — `DoubleVar.set(None)` does not raise, it stores
    the literal `'None'` and detonates at an arbitrary later `get()`, inside a Tk
    trace where nothing Python can see it.
    """
    with pytest.raises(BootstackError, match="no way to hold an empty value"):
        bs.Slider(signal=make_signal(), parent=app)


def test_a_subclass_of_a_refused_type_is_refused_too(app):
    """An `IntEnum` dtype must not slip the guard the plain `int` hits.

    The guard read `self._type in (bool, int, float)`, so a declared `IntEnum`
    missed it, took an `IntVar` anyway, and reported `sig() == 0` while
    `allows_empty` said True -- a real value posing as empty, with `clear()`
    throwing inside a Tk callback afterwards. Same defect as round 2's finding 1,
    re-entered through a subclass.
    """
    class Level(IntEnum):
        LOW = 0
        HIGH = 1

    with pytest.raises(BootstackError, match="no way to hold an empty value"):
        bs.Slider(signal=bs.Signal(None, allow_empty=True, dtype=Level), parent=app)


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
