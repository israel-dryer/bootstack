"""#461 — a `SelectButton`'s `signal=` binds the option's VALUE, not its label.

The same one-line wiring defect #458 fixed in `Select`, in the sibling widget:
`signal=` was mapped onto the internal `textsignal=`, which backs the variable
holding the option's TEXT. So the signal was the only surface on the widget
speaking label-space, while `value=`, `.value`, `.selection` and the
`<<Change>>` payload all speak value-space — and the docstring promised the
value.

Measured on `main` before the fix, options `[('One','1'), ('Two','2'), ...]`:

    signal=Signal('Two')   text='Two'  value='2'  selection='2'    <- worked, undocumented
    signal=Signal('2')     text='2'    value='2'  selection=None   <- documented, broken
    sb.value = '3'         signal='Three'                          <- write-back leaked the label

`signal=` is value-space now. Seeding with a label raises, which is a BEHAVIOR
CHANGE for the only spelling that worked — deliberate, and the same call taken
for `Select` in #458.

Every test here fails against pre-fix source for a BEHAVIORAL reason. `signal=`
was accepted before, so nothing raises `AttributeError` either way; a failure
means the button showed or reported the wrong option.

Assertions are on the values carried, never on event counts: `SelectButton`
emits `<<Change>>` more than once per set, a pre-existing `StringVar` quirk
noted at `test_select_options.py:290`.
"""
import bootstack as bs
import pytest

# Decoupled: label differs from the stored value. The only shape where the two
# spaces can disagree, and the shape the issue measured.
DECOUPLED = [("One", "1"), ("Two", "2"), ("Three", "3")]

# Plain: the label IS the value, so the two spaces coincide. The control
# population — every `signal=` usage in our own docs is this shape.
PLAIN = ["One", "Two", "Three"]


# --------------------------------------------------------------------------
# Seeding — which space does the signal speak?
# --------------------------------------------------------------------------

def test_a_seeded_signal_selects_the_option_it_names(app):
    """The issue, verbatim: Signal('2') must select Two, not display '2'.

    Pre-fix this left `selection` at `None` indefinitely — the button never
    considered anything selected.
    """
    sb = bs.SelectButton(options=list(DECOUPLED), signal=bs.Signal("2"))

    assert sb.text == "Two"
    assert sb.value == "2"
    assert sb.selection["text"] == "Two"


def test_signal_and_value_seed_a_button_identically(app):
    """`value=` and `signal=` are two doors to the same state.

    Pinned as a pair rather than as two separate expectations: the defect was
    precisely that the two doors disagreed, so the equality IS the contract.
    """
    by_value = bs.SelectButton(options=list(DECOUPLED), value="2")
    by_signal = bs.SelectButton(options=list(DECOUPLED), signal=bs.Signal("2"))

    assert by_value.text == by_signal.text
    assert by_value.value == by_signal.value
    assert by_value.selection == by_signal.selection


def test_a_label_seeded_signal_raises_like_the_value_door(app):
    """The migration, pinned against BOTH doors so they cannot drift apart.

    Seeding with a label is what worked pre-fix. It now raises — and raises the
    same way `value='Two'` already did, which is the whole justification for
    not softening it. If a later change makes one door tolerant, this fails.
    """
    with pytest.raises(ValueError, match="not one of the options"):
        bs.SelectButton(options=list(DECOUPLED), signal=bs.Signal("Two"))

    with pytest.raises(ValueError, match="not one of the options"):
        bs.SelectButton(options=list(DECOUPLED), value="Two")


# --------------------------------------------------------------------------
# The live binding, both directions
# --------------------------------------------------------------------------

def test_a_signal_write_moves_the_selection_on_decoupled_options(app):
    signal = bs.Signal("1")
    sb = bs.SelectButton(options=list(DECOUPLED), signal=signal)

    signal.set("3")
    app.tk.update()

    assert sb.text == "Three"
    assert sb.value == "3"
    assert sb.selection["value"] == "3"


def test_a_signal_write_moves_the_selection_on_plain_options(app):
    """Needs no decoupling — guards the binding itself, not the value map."""
    signal = bs.Signal("One")
    sb = bs.SelectButton(options=list(PLAIN), signal=signal)

    signal.set("Three")
    app.tk.update()

    assert sb.text == "Three"
    assert sb.value == "Three"


def test_setting_value_pushes_the_value_not_the_label_to_the_signal(app):
    """The write-back half: the signal receives '3', not the label 'Three'.

    Pre-fix a caller reading the signal and a caller reading `.value` got
    different things for the same selection.
    """
    signal = bs.Signal("1")
    sb = bs.SelectButton(options=list(DECOUPLED), signal=signal)

    sb.value = "3"
    app.tk.update()

    assert signal() == "3"
    assert sb.value == "3"


def test_the_signal_round_trips_through_a_second_button(app):
    """Two buttons on one signal is what a Signal is FOR; it must stay coherent."""
    signal = bs.Signal("1")
    first = bs.SelectButton(options=list(DECOUPLED), signal=signal)
    second = bs.SelectButton(options=list(DECOUPLED), signal=signal)

    first.value = "2"
    app.tk.update()

    assert second.value == "2"
    assert second.text == "Two"
    assert signal() == "2"


def test_plain_options_are_unaffected_by_the_space_change(app):
    """The control population: label == value, so nothing can diverge.

    Every `signal=` usage in our own docs is this shape, which is why the
    migration is narrow.
    """
    signal = bs.Signal("Two")
    sb = bs.SelectButton(options=list(PLAIN), signal=signal)

    assert sb.text == "Two"
    assert sb.value == "Two"

    sb.value = "One"
    app.tk.update()
    assert signal() == "One"


def test_int_valued_options_round_trip(app):
    """A non-str value must survive the binding — `signal=` is no longer str-only."""
    signal = bs.Signal(2)
    sb = bs.SelectButton(options=[("One", 1), ("Two", 2), ("Three", 3)], signal=signal)

    assert sb.text == "Two"
    assert sb.value == 2

    sb.value = 3
    app.tk.update()
    assert signal() == 3


# --------------------------------------------------------------------------
# Change events
# --------------------------------------------------------------------------

def test_seeding_a_signal_does_not_fire_change(app):
    """Construction is not a change, and `value=` does not fire one either.

    `SelectButton` needs no seed suppression to get this — its internal emits
    with `when='now'`, so the seed is delivered before any handler can be
    bound, where `Select` had to suppress a QUEUED emit (#458) and `TimeField`
    still does (#459). Pinned because that difference is invisible in the
    source and a later change to the emit's `when=` would silently break it.
    """
    sb = bs.SelectButton(options=list(DECOUPLED), signal=bs.Signal("2"))
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))
    app.tk.update()

    assert seen == []


def test_a_signal_write_still_fires_change_in_value_space(app):
    """The other half of the test above: seeding is quiet, real writes are not.

    Guards the failure where suppressing the seed silences the widget outright.
    Asserts the values carried, not the count — `SelectButton` emits more than
    once per set (pre-existing `StringVar` quirk).
    """
    signal = bs.Signal("1")
    sb = bs.SelectButton(options=list(DECOUPLED), signal=signal)
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))

    signal.set("2")
    app.tk.update()
    signal.set("3")
    app.tk.update()

    assert seen, "a signal write must announce the new selection"
    assert set(seen) == {"2", "3"}
    assert seen[-1] == "3"


# --------------------------------------------------------------------------
# Identity and teardown
# --------------------------------------------------------------------------

def test_the_signal_property_returns_the_callers_own_object(app):
    """#461's secondary observation.

    Pre-fix the property forwarded to the internal's `textsignal`, a DIFFERENT
    `Signal` wrapping the same variable, so `sb.signal is sig` was False.
    """
    signal = bs.Signal("1")
    sb = bs.SelectButton(options=list(DECOUPLED), signal=signal)

    assert sb.signal is signal


def test_signal_is_none_when_nothing_is_bound(app):
    """The property must not manufacture one.

    Pre-fix it returned a live `Signal` for every button ever built, which is
    what put `SelectButton` in #460's population of eight.
    """
    sb = bs.SelectButton(options=list(DECOUPLED), value="1")

    assert sb.signal is None


def test_destroying_the_button_releases_the_signal_subscription(app):
    """A `Signal` usually outlives the widgets bound to it.

    Without the release the subscription pins a destroyed button in memory and
    a later write drives a widget that is gone. The write below must be
    harmless — the assertion is that it does not raise.
    """
    signal = bs.Signal("1")
    sb = bs.SelectButton(options=list(DECOUPLED), signal=signal)
    assert sb._value_sub is not None

    sb.destroy()
    app.tk.update()

    assert sb._value_sub is None

    signal.set("2")
    app.tk.update()
    assert signal() == "2"


# --------------------------------------------------------------------------
# Off-list values — NOT this issue's to decide
# --------------------------------------------------------------------------

def test_an_off_list_signal_value_raises_like_the_value_door(app):
    """`SelectButton` rejects an off-list value where `Select` displays it.

    That divergence is #369's, not this fix's: it already records
    `SelectButton` as raising on both doors, and asks the selection family for
    ONE decision rather than four patches. Pinned so the fix's effect on the
    signal door is visible — the raise, deliberately, NOT the state it leaves
    behind (the signal moves and the button does not, which is part of what
    #369 has to settle).
    """
    signal = bs.Signal("1")
    bs.SelectButton(options=list(DECOUPLED), signal=signal)

    with pytest.raises(ValueError, match="not one of the options"):
        signal.set("99")
