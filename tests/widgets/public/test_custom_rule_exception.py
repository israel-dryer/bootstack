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
from bootstack.validation.validation_rules import ValidationRule


class _Domain(Exception):
    """A user-defined exception, to prove the guard is not TypeError-shaped."""


def _rule(func, message="rule says no", **kw):
    return ValidationRule("custom", func=func, message=message, **kw)


# --- the defect itself ------------------------------------------------------

@pytest.mark.parametrize("value", [None, "", "6"])
def test_a_func_that_cannot_judge_reports_invalid_instead_of_raising(value):
    # `lambda v: v > 5` is the issue's own func. Each of these values reaches it
    # as a type it cannot compare, so before the fix this raised out of validate().
    result = _rule(lambda v: v > 5, "must exceed 5").validate(value)

    assert result.is_valid is False
    assert result.message == "must exceed 5"


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
    assert field.error() == "must exceed 5"


def test_the_blur_trigger_control_a_failing_func_is_visible(shown_app):
    # CONTROL for the test above. Without it, an arm whose trigger never ran is
    # indistinguishable from a fix that works -- the first probe written for this
    # issue failed exactly that way, and its quiet arms meant nothing.
    field = _blur_field(shown_app, lambda v: False)

    assert field._internal._entry.validate(field.value, "blur") is False
    assert field.valid() is False


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
