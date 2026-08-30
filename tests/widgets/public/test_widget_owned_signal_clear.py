"""A signal the framework made for a widget can be emptied, or says why not (#484).

Six public widgets expose a `.signal` the caller never constructed. All six got
`allow_empty=False`, so `clear()` raised — advising `allow_empty=True to
Signal()`, a constructor the caller cannot reach. There was no edit that followed
the advice.

The framework now declares empty on the signals it builds for a widget whose
variable has an empty member, which is the four entry-backed text fields. A
`Slider` and a `Checkbox` still refuse, and correctly: their variables hold a
`float` and a `bool`, neither of which has an empty member, and #390's floor
already refuses to bind an empty-capable signal to them. What changes there is
the sentence, which now also offers a way out that does not need a constructor.

⚠ One sentence serves both owners rather than branching on provenance. The old
advice was not merely unreachable for a widget's own signal — following it landed
on the binding refusal, which `test_signal_empty.py` covers at length.

⚠ `field.value` reads `None` after a clear while the bound signal reads `''`.
Measured against `main`: the shipped `TextField.clear()` already produced exactly
that state, so it is pre-existing and this change only adds a second door onto it.
Deliberately not asserted here — pinning it would read as sanctioning it.
"""
import pytest

import bootstack as bs


TEXT_FIELDS = [
    pytest.param(bs.TextField, id="TextField"),
    pytest.param(bs.PasswordField, id="PasswordField"),
    pytest.param(bs.PathField, id="PathField"),
    pytest.param(bs.SpinnerField, id="SpinnerField"),
]

REFUSING = [
    pytest.param(lambda app: bs.Slider(parent=app), "float", id="Slider"),
    pytest.param(lambda app: bs.Checkbox("x", parent=app), "bool", id="Checkbox"),
]


# --------------------------------------------------------------------------
# The four that can now be emptied
# --------------------------------------------------------------------------

@pytest.mark.parametrize("factory", TEXT_FIELDS)
def test_a_text_fields_own_signal_declares_that_it_can_be_empty(app, factory):
    """The gate, read directly — `''` is a real member of `str`, so it may."""
    field = factory(parent=app)
    app.tk.update()

    assert field.signal.allows_empty is True


@pytest.mark.parametrize("factory", TEXT_FIELDS)
def test_clearing_a_text_fields_own_signal_empties_the_field(app, factory):
    """The defect as reported: this raised, naming a constructor never called."""
    field = factory(parent=app)
    field.value = "seeded"
    app.tk.update()
    assert field.tk.get() == "seeded", "precondition: the seed reached the entry"
    seen: list = []
    field.signal.subscribe(lambda v: seen.append(v))

    field.signal.clear()
    app.tk.update()

    assert field.signal() == ""
    assert field.tk.get() == ""
    assert seen == [""]


# --------------------------------------------------------------------------
# The two that still refuse, and the sentence they refuse with
# --------------------------------------------------------------------------

@pytest.mark.parametrize("factory,typename", REFUSING)
def test_a_widget_whose_variable_has_no_empty_still_refuses(app, factory, typename):
    """Unchanged by design — a slider has a position and a checkbox a state."""
    widget = factory(app)
    app.tk.update()

    with pytest.raises(TypeError) as excinfo:
        widget.signal.clear()

    assert str(excinfo.value).startswith(f"Expected {typename}, got NoneType.")


@pytest.mark.parametrize("factory,typename", REFUSING)
def test_the_refusal_offers_something_a_caller_without_the_constructor_can_do(
        app, factory, typename):
    """The half of #484 the gate cannot fix: the advice was unfollowable here.

    The old sentence read `Pass allow_empty=True to Signal()`, and a caller who
    followed it landed on a second error — the binding refuses an empty-capable
    signal on these widgets. Setting a value is the way out that always works.
    """
    widget = factory(app)
    app.tk.update()

    with pytest.raises(TypeError, match="set the value directly"):
        widget.signal.clear()


@pytest.mark.parametrize("factory,typename", REFUSING)
def test_the_refusal_advises_nothing_the_widget_cannot_do(app, factory, typename):
    """Neither widget has a `clear()`, so advising one would raise `AttributeError`.

    Conditional rather than `not hasattr`: adding `Slider.clear()` later is not a
    defect, but shipping a message that assumes it before it exists is.
    """
    widget = factory(app)
    app.tk.update()

    with pytest.raises(TypeError) as excinfo:
        widget.signal.clear()

    if "clear()" in str(excinfo.value):
        assert hasattr(widget, "clear"), "the message advises a method the widget lacks"


# --------------------------------------------------------------------------
# Controls — what a wrong implementation of the gate would break
# --------------------------------------------------------------------------

@pytest.mark.parametrize("factory,typename", REFUSING)
def test_both_refusing_widgets_still_construct_and_expose_a_readable_signal(
        app, factory, typename):
    """⚠ The control that matters most.

    A "simplification" of the gate to an unconditional `allow_empty=True` passes
    every other test in this file while making both widgets unconstructible — the
    framework would hand them a signal its own binding guard rejects.
    """
    widget = factory(app)
    app.tk.update()

    assert widget.signal() is not None
    assert widget.signal.allows_empty is False


def test_a_caller_owned_signal_can_still_be_empty_whatever_its_type(app):
    """The gate marks what the framework builds; it must not reach the caller's."""
    sig = bs.Signal(0.0, allow_empty=True)

    sig.clear()

    assert sig() is None


def test_one_sentence_serves_both_owners(app):
    """The decision, pinned: the message does not branch on who made the signal.

    A caller who can reach the constructor and one who cannot get the same
    sentence, because it carries both ways out. Branching would need `Signal` to
    know its own provenance, which is a concept it otherwise does not have — and
    a branch on the *type* instead would be wrong for the caller, since
    `Signal(0.0, allow_empty=True)` is legal on its own.
    """
    slider = bs.Slider(parent=app)
    app.tk.update()

    with pytest.raises(TypeError) as widget_owned:
        slider.signal.clear()
    with pytest.raises(TypeError) as caller_owned:
        bs.Signal(0.0).clear()

    assert str(widget_owned.value) == str(caller_owned.value)
    assert "allow_empty=True" in str(caller_owned.value)
