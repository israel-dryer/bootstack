"""#458 — a `Select`'s `signal=` binds the option's VALUE, not its display text.

Reported externally against 0.3.2: with decoupled `(text, value)` options,
`Select(signal=Signal('2'))` displayed `2` where `Select(value='2')` displayed
`Two`.

The root cause was one wiring line — `signal=` was mapped onto the internal
`textsignal=`, which installs the `Signal`'s Tk variable *as the entry's
textvariable*. Writes therefore landed straight in the display text, bypassing
both the value-to-text map and the entry's commit path. That produced a second,
wider symptom the report did not mention: a signal write moved the display but
not the selection, so `.value`/`.selection` went stale and no `<<Change>>`
fired — on plain `list[str]` options too.

Every test here fails against pre-fix source for a BEHAVIORAL reason. `signal=`
was accepted before, so nothing raises `AttributeError` either way; a failure
means the field showed or reported the wrong option.
"""
import bootstack as bs
import pytest

# Decoupled: display text differs from the stored value. This is the shape the
# report used and the only shape where text-space and value-space can disagree.
DECOUPLED = [("One", "1"), ("Two", "2"), ("Three", "3")]

# Plain: text IS the value, so the two spaces coincide. The control population.
PLAIN = ["One", "Two", "Three"]


def _shown(sel) -> str:
    """What the user actually sees, which is what the report was about."""
    return sel._internal.entry_widget.get()


# --------------------------------------------------------------------------
# The reported symptom
# --------------------------------------------------------------------------

def test_a_seeded_signal_displays_the_option_text_not_its_value(app):
    """The report, verbatim: Signal('2') must select Two, not display '2'."""
    sel = bs.Select(options=list(DECOUPLED), signal=bs.Signal("2"))

    assert _shown(sel) == "Two"
    assert sel.value == "2"
    assert sel.selection["text"] == "Two"


def test_signal_and_value_seed_a_field_identically(app):
    """`value=` and `signal=` are two doors to the same state.

    Pinned as a pair rather than as two separate expectations: the defect was
    precisely that the two doors disagreed, so the equality IS the contract.
    """
    by_value = bs.Select(options=list(DECOUPLED), value="2")
    by_signal = bs.Select(options=list(DECOUPLED), signal=bs.Signal("2"))

    assert _shown(by_value) == _shown(by_signal)
    assert by_value.value == by_signal.value


# --------------------------------------------------------------------------
# The unreported symptom — wider, because it needs no decoupling
# --------------------------------------------------------------------------

def test_a_signal_write_moves_the_selection_on_plain_options(app):
    """The half the report missed: this needs no decoupled options at all.

    Pre-fix the display moved to 'Three' while `.value` stayed 'One' — the
    field showed one option and reported another, indefinitely.
    """
    signal = bs.Signal("One")
    sel = bs.Select(options=list(PLAIN), signal=signal)

    signal.set("Three")
    app.tk.update()

    assert _shown(sel) == "Three"
    assert sel.value == "Three"
    assert sel.selection["text"] == "Three"


def test_a_signal_write_moves_the_selection_on_decoupled_options(app):
    signal = bs.Signal("1")
    sel = bs.Select(options=list(DECOUPLED), signal=signal)

    signal.set("3")
    app.tk.update()

    assert _shown(sel) == "Three"
    assert sel.value == "3"
    assert sel.selection["text"] == "Three"


def test_a_signal_write_fires_change_once(app):
    """A selection that moves must be announced, and announced exactly once.

    Pre-fix a signal write fired nothing, because it never reached the commit
    path. The 'once' half guards the opposite failure — the two-way binding
    feeding its own write back as a second change.
    """
    signal = bs.Signal("1")
    sel = bs.Select(options=list(DECOUPLED), signal=signal)
    seen: list = []
    sel.on_change(lambda e: seen.append(e.value))

    signal.set("2")
    app.tk.update()
    signal.set("3")
    app.tk.update()

    assert seen == ["2", "3"]


def test_seeding_a_signal_does_not_fire_change(app):
    """Construction is not a change — and `value=` does not fire one either.

    Non-obvious mechanism, which is why this is pinned: the seed's `<<Change>>`
    is QUEUED, so a handler bound on the line after the constructor still
    receives it once the loop turns. The reporter's own snippet binds
    `on_change` to `bs.toast`, so a seed-time emit would toast on startup.
    """
    sel = bs.Select(options=list(DECOUPLED), signal=bs.Signal("2"))
    seen: list = []
    sel.on_change(lambda e: seen.append(e.value))
    app.tk.update()

    assert seen == []


# --------------------------------------------------------------------------
# The write-back direction
# --------------------------------------------------------------------------

def test_setting_value_pushes_the_value_to_the_signal(app):
    """The signal receives '2', not the label 'Two'.

    Pre-fix this wrote the display text, which made the binding lossy: the
    signal could not be fed back into another `Select` and land on the same
    option.
    """
    signal = bs.Signal("1")
    sel = bs.Select(options=list(DECOUPLED), signal=signal)

    sel.value = "2"
    app.tk.update()

    assert signal() == "2"
    assert _shown(sel) == "Two"


def test_the_signal_round_trips_through_a_second_select(app):
    """The practical consequence of value-space: one signal, two fields agree."""
    signal = bs.Signal("2")
    first = bs.Select(options=list(DECOUPLED), signal=signal)
    second = bs.Select(options=list(DECOUPLED), signal=signal)

    assert _shown(first) == _shown(second) == "Two"

    first.value = "3"
    app.tk.update()

    assert second.value == "3"
    assert _shown(second) == "Three"


# --------------------------------------------------------------------------
# Invariants that must NOT move
# --------------------------------------------------------------------------

def test_plain_options_are_unaffected(app):
    """The control that scopes the change.

    Where text == value the two readings coincide, so this population must
    behave exactly as it did before. If this ever fails, the fix reached
    further than the defect.
    """
    signal = bs.Signal("Two")
    sel = bs.Select(options=list(PLAIN), signal=signal)

    assert _shown(sel) == "Two"
    assert sel.value == "Two"
    assert signal() == "Two"


def test_an_off_list_signal_value_is_displayed_and_does_not_raise(app):
    """#368's retired-value contract survives the signal path.

    A fixed option list constrains what a USER can pick; it is not a schema for
    what the program may supply. A stored value that has since left the list
    still displays rather than crashing the editor that opened it.
    """
    sel = bs.Select(options=list(DECOUPLED), signal=bs.Signal("99"))

    assert _shown(sel) == "99"
    assert sel.value == "99"


def test_int_valued_options_round_trip(app):
    """`_push_to_signal` reconciles numeric types; a non-str value must survive."""
    signal = bs.Signal(2)
    sel = bs.Select(options=[("One", 1), ("Two", 2)], signal=signal)

    assert _shown(sel) == "Two"
    assert sel.value == 2

    signal.set(1)
    app.tk.update()
    assert _shown(sel) == "One"


def test_read_only_is_still_honored_with_a_bound_signal(app):
    """#453's derived read-only state must not be defeated by the binding.

    The value setter brackets its write with the entry's readonly state, and
    the signal now drives that same setter — so this pins the interaction
    rather than assuming it. The write below is the point: the constructor's
    seed crosses that bracket once, but the path this branch adds is a LATER
    write arriving from the signal.

    The entry state is asserted directly because neither of the other two
    checks can see it. `read_only` reads the stored SETTING, which #453
    deliberately decoupled from the entry state, and the shown text is
    correct either way — so a setter that left the entry `!readonly` after
    its write would pass both while the field was silently editable.
    """
    signal = bs.Signal("1")
    sel = bs.Select(options=list(DECOUPLED), signal=signal, read_only=True)

    assert sel.read_only is True

    signal.set("3")
    app.tk.update()

    assert _shown(sel) == "Three"
    assert sel.read_only is True
    assert sel._internal.entry_widget.instate(["readonly"])


def test_a_signal_seeded_after_value_wins(app):
    """Passing both is legal; the signal seeds last and therefore wins.

    Pinned so the precedence is a decision on the record rather than an
    accident of statement order in the constructor.
    """
    sel = bs.Select(options=list(DECOUPLED), value="1", signal=bs.Signal("3"))

    assert _shown(sel) == "Three"
    assert sel.value == "3"


def test_textsignal_is_rejected_and_names_the_replacement(app):
    """Pre-fix `textsignal=` fell into **kwargs and was silently discarded.

    Nobody can be relying on it, so refusing it costs nothing and stops the
    old spelling from failing silently. Mirrors `TimeField`.
    """
    with pytest.raises(TypeError, match="signal="):
        bs.Select(options=list(DECOUPLED), textsignal=bs.Signal("Two"))


def test_destroying_the_field_releases_the_signal_subscription(app):
    """A `Signal` usually outlives the widgets bound to it.

    Without the release, the subscription pins a destroyed field (and
    everything it references) in memory, and a later write drives a widget that
    is gone. The write below must be harmless — the assertion is that it does
    not raise.
    """
    signal = bs.Signal("1")
    sel = bs.Select(options=list(DECOUPLED), signal=signal)
    assert sel._value_sub is not None

    sel.destroy()
    app.tk.update()

    assert sel._value_sub is None

    signal.set("2")
    app.tk.update()
    assert signal() == "2"
