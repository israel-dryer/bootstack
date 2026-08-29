"""#467 -- a `custom` rule whose func raises must not leave the field stale.

The `range` branch catches `TypeError` from an incomparable pair and reports the
value invalid; the `custom` branch called `func(value)` with no guard, so a func
that could not judge its value propagated instead. On the automatic trigger there
is no caller: the exception unwinds into the Tk event loop and the field keeps
whatever validity it had, so the end user sees a field that quietly stopped
validating.

⚠ Reaching the automatic path needs a deliberate `trigger="blur"`/`"always"` --
`custom` defaults to `"manual"`. The issue's own reproduction omits it and so does
not fire; see the 2026-08-29 comment on #467.
"""
import pytest

import bootstack as bs
from bootstack.validation.validation_rules import UNCHECKABLE_MESSAGE, ValidationRule


class _Domain(Exception):
    """A user-defined exception, to prove the guard is not TypeError-shaped."""


def _rule(func, message="rule says no", **kw):
    return ValidationRule("custom", func=func, message=message, **kw)


def _uncheckable(expected):
    """What the end user sees when the predicate raised on a rule with a message."""
    return f"Could not check this value (expected: {expected})."


# --- the defect itself ------------------------------------------------------

@pytest.mark.parametrize("value", [None, "", "6"])
def test_a_func_that_cannot_judge_reports_invalid_instead_of_raising(value):
    # `lambda v: v > 5` is the issue's own func. Each of these values reaches it
    # as a type it cannot compare, so before the fix this raised out of validate().
    result = _rule(lambda v: v > 5, "must exceed 5").validate(value)

    assert result.is_valid is False
    # NOT the rule's own message. "must exceed 5" describes a condition, and the
    # predicate never managed to judge this value against it -- a field reading
    # "must exceed 5" while holding 6 tells the end user something false.
    # The rule's message is demoted to an EXPECTATION, never returned as the
    # verdict: "must exceed 5" about a field holding 6 is plainly false, and the
    # predicate never judged it. Throwing the message away entirely would leave
    # the user with nothing to act on, so it is carried, not asserted.
    assert result.message == _uncheckable("must exceed 5")
    assert result.message != "must exceed 5"


def test_a_func_that_can_judge_is_untouched():
    # The ordinary case must not move: a comparable value still decides normally.
    assert _rule(lambda v: v > 5).validate(6).is_valid is True
    assert _rule(lambda v: v > 5).validate(4).is_valid is False


# --- the breadth of the catch ----------------------------------------------

@pytest.mark.parametrize(
    "exc", [TypeError("t"), AttributeError("a"), KeyError("k"), ValueError("v"), _Domain("d")]
)
def test_any_exception_from_the_func_is_absorbed(exc):
    # `range` only ever compares, so `except TypeError` bounds it. A user func can
    # raise anything -- narrowing this catch re-opens #467 for every other type.
    def raises(_value):
        raise exc

    assert _rule(raises).validate("x").is_valid is False


def test_a_keyboard_interrupt_still_propagates():
    # The control for the choice of `Exception` over `BaseException`: a user
    # interrupt must never be swallowed as "this value is invalid".
    def interrupt(_value):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _rule(interrupt).validate("x")


# --- the automatic path, which is where the harm was ------------------------

def _blur_field(app, func, *, value="6"):
    """Build a TextField with a custom rule on the AUTOMATIC blur trigger."""
    with app:
        field = bs.TextField(value=value)
        field.add_validation_rule(
            "custom", func=func, message="must exceed 5", trigger="blur"
        )
    return field


def test_the_blur_trigger_leaves_a_defined_validity(shown_app):
    # THE REGRESSION TEST. Before the fix this ended `valid is True` -- the rule
    # blew up inside the debounced after() callback and the field kept its old
    # validity with nothing to show the user.
    field = _blur_field(shown_app, lambda v: v > 5)

    assert field._internal._entry.validate(field.value, "blur") is False
    assert field.valid() is False
    assert field.error() == _uncheckable("must exceed 5")


def test_the_blur_trigger_control_a_failing_func_is_visible(shown_app):
    # CONTROL for the test above. Without it, an arm whose trigger never ran is
    # indistinguishable from a fix that works -- the first probe written for this
    # issue failed exactly that way, and its quiet arms meant nothing.
    field = _blur_field(shown_app, lambda v: False)

    assert field._internal._entry.validate(field.value, "blur") is False
    assert field.valid() is False
    # And it carries the RULE'S message, where a raise carries UNCHECKABLE_MESSAGE.
    # That difference is the whole point: a verdict and a crash must not look the
    # same to the end user.
    assert field.error() == "must exceed 5"


def test_the_blur_trigger_control_a_passing_func_stays_valid(shown_app):
    # The other half of the control: the trigger runs and can also report valid,
    # so `valid is False` above is the rule deciding, not a field stuck invalid.
    field = _blur_field(shown_app, lambda v: True)

    assert field._internal._entry.validate(field.value, "blur") is True
    assert field.valid() is True


# --- the trigger default the issue's repro missed ---------------------------

def test_custom_rules_still_default_to_the_manual_trigger():
    # Pins the fact that narrows this issue: `custom` is not evaluated on an
    # automatic trigger unless the caller asks for one. If this default ever
    # changes, #467's blast radius changes with it.
    assert _rule(lambda v: True).trigger == "manual"


# --- the author-facing half: absorbing must not be silent (review round 1) ---

def test_the_first_raise_is_reported_on_stderr(capsys):
    # Round 1 finding F1. Before this, the guard wrote nothing unless
    # BOOTSTACK_DEBUG was set -- so the branch was QUIETER than the code it
    # replaced, which got a traceback for free from Tk's
    # report_callback_exception. A func that raises is always a defect in the
    # author's own code; the framework must not be the thing that hides it.
    rule = _rule(lambda v: v > 5)

    rule.validate("6")

    err = capsys.readouterr().err
    assert "custom" in err
    assert "TypeError" in err
    assert "BOOTSTACK_DEBUG" in err


def test_the_report_does_not_repeat_for_the_same_rule(capsys):
    # The one-shot latch is load-bearing, not cosmetic: a rule with
    # trigger='always' runs on every keystroke through the debounced after(),
    # so an unconditional print floods the console as the user types.
    rule = _rule(lambda v: v > 5)
    rule.validate("6")
    capsys.readouterr()

    rule.validate("7")
    rule.validate("8")

    assert capsys.readouterr().err == ""


def test_a_func_that_does_not_raise_reports_nothing(capsys):
    # CONTROL for the two above: the channel is quiet for the ordinary case, so
    # a message there is the guard firing rather than noise from construction.
    _rule(lambda v: False).validate("6")
    _rule(lambda v: True).validate("6")

    assert capsys.readouterr().err == ""


def test_a_value_whose_repr_raises_does_not_escape_the_guard():
    # Round 1 finding F2. The diagnostic used to interpolate `{value!r}` into an
    # f-string built eagerly inside the except block, so a hostile __repr__ threw
    # straight back out of the guard -- #467 re-opened by the code fixing it. A
    # rule sees the field's TYPED value, and a Select's value kind is whatever
    # its options carry, so user objects reach here.
    class Hostile:
        def __repr__(self):
            raise RuntimeError("repr exploded")

    assert _rule(lambda v: v > 5).validate(Hostile()).is_valid is False


def test_a_value_whose_repr_raises_does_not_escape_with_debug_on(monkeypatch):
    # The other arm of the same guard: with BOOTSTACK_DEBUG set,
    # debug_log_exception actually runs and prints, and the repr still must not
    # escape.
    monkeypatch.setenv("BOOTSTACK_DEBUG", "1")

    class Hostile:
        def __repr__(self):
            raise RuntimeError("repr exploded")

    assert _rule(lambda v: v > 5).validate(Hostile()).is_valid is False


def test_a_raise_and_a_verdict_do_not_look_the_same():
    # The two ways a custom rule reports invalid must be distinguishable. Before
    # this, both said "must exceed 5" -- including for the value 6, which does
    # exceed 5, because the predicate had crashed rather than judged.
    raised = _rule(lambda v: v > 5, "must exceed 5").validate("6")
    judged = _rule(lambda v: v > 5, "must exceed 5").validate(4)

    assert raised.is_valid is judged.is_valid is False
    assert raised.message == _uncheckable("must exceed 5")
    assert judged.message == "must exceed 5"
    assert raised.message != judged.message


def test_a_rule_with_no_message_falls_back_to_the_bare_sentence():
    # Composing an author message that was never supplied would reach for
    # _default_message() and produce "Could not check this value (expected:
    # Invalid value.)" -- nonsense. The composer reads self.message, which is
    # empty here, not the resolved message.
    rule = ValidationRule("custom", func=lambda v: v > 5)

    assert rule.validate("6").message == UNCHECKABLE_MESSAGE
    assert "expected" not in rule.validate("6").message


def test_the_expectation_is_not_double_punctuated():
    # An author message that already ends in a period must not produce
    # "(expected: Enter a valid email address.)." -- two stops, one inside the
    # parenthesis and one outside.
    rule = _rule(lambda v: v > 5, "Enter a valid email address.")

    assert rule.validate("6").message == _uncheckable("Enter a valid email address")
    assert ".)." not in rule.validate("6").message
