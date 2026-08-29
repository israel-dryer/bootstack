import re
import sys
from typing import Callable

from bootstack._runtime.utility import debug_log_exception
from bootstack.validation.types import RuleTriggerType, RuleType
from bootstack.validation.validation_result import ValidationResult


# Shown when a `'custom'` rule's func raised instead of returning a verdict, and
# the rule carries no message of its own. See `_uncheckable_message`.
UNCHECKABLE_MESSAGE = "Could not check this value."


# Rules that operate on a text value; meaningless on a typed (number/date/time)
# value. The field rejects these at attach time when it does not hold text.
TEXT_RULES = frozenset({"stringLength", "pattern", "email"})

# Rules that operate on an orderable typed value (number, date, or time).
ORDERED_RULES = frozenset({"range"})


def rule_applies_to_kind(rule_type: str, kind: str) -> bool:
    """Whether a rule type can validate a field holding the given value kind.

    Args:
        rule_type: The rule name (e.g. `'stringLength'`, `'range'`).
        kind: The field's value kind — `'text'`, `'number'`, `'date'`, or
            `'time'`.

    Returns:
        `True` if the rule applies. Text rules apply only to text fields;
        `'range'` applies only to ordered (number/date/time) fields; the
        remaining rules (`'required'`, `'compare'`, `'custom'`) apply to any.
    """
    if rule_type in TEXT_RULES:
        return kind == "text"
    if rule_type in ORDERED_RULES:
        return kind in ("number", "date", "time")
    return True


def _is_empty(value: object) -> bool:
    """Whether a field holds nothing, for rules that only shape a value.

    Matches the emptiness test `range` uses: `None` or the empty string. A
    whitespace-only entry is real input — `stringLength` should still measure
    it — so only `required` treats blank text as absent.
    """
    return value is None or value == ""


def _as_text(value: object) -> str:
    """Coerce a value to text for the string rules.

    The string rules (`stringLength`, `pattern`, `email`) operate on text. When
    one is applied to a typed value (a number or date), coerce rather than crash;
    the rule taxonomy rejects that misuse at attach time, this is the last-ditch
    guard. `None` (an empty field) becomes the empty string.
    """
    if isinstance(value, str):
        return value
    return "" if value is None else str(value)


class ValidationRule:
    """A single validation rule that can be applied to a string value.

    Supports the built-in rule types `'required'`, `'email'`,
    `'stringLength'`, `'pattern'`, `'compare'`, and `'custom'`, and carries a
    trigger policy that controls when the rule is evaluated.

    Attributes:
        type (RuleType): The validation rule type.
        message (str): Custom error message; if empty a default is generated.
        trigger (RuleTriggerType): When the rule fires — `'always'`, `'key'`,
            `'blur'`, or `'manual'`.
        params (dict): Additional parameters specific to the rule type
            (e.g., `min`/`max` for `'stringLength'`, `pattern` for `'pattern'`,
            `other_field` for `'compare'`, `func` for `'custom'`).
    """

    def __init__(
            self,
            rule_type: RuleType,
            message: str = "",
            **kwargs
    ):
        """Create a validation rule.

        Args:
            rule_type: The type of validation to apply.
            message: Custom error message. If empty, a sensible default is used.
            **kwargs: Rule-specific parameters.  Pass `trigger` to override the
                default trigger policy; all other keys are stored in `params`
                (e.g., `min=3, max=20` for `'stringLength'`, `pattern=r'\\d+'`
                for `'pattern'`, `func=callable` for `'custom'`).
        """
        self.type = rule_type
        self.message = message
        self.trigger = kwargs.pop('trigger', self._default_trigger())
        self.params = kwargs
        # One-shot latch for `_report_func_error`; see its docstring.
        self._func_error_reported = False

    def validate(self, value: str) -> ValidationResult:
        """Apply this rule to a value and return the result.

        Args:
            value: The string value to validate.

        Returns:
            A ValidationResult with `is_valid=True` on success or `is_valid=False`
            with an error message on failure.

            A `'custom'` rule whose `func` raises is reported invalid rather than
            allowed to propagate, so a predicate that cannot judge a value does
            not leave the field's validity stale. Its message is
            "Could not check this value (expected: …)", carrying the rule's own
            `message` as an expectation rather than as a verdict — the check never
            ran, so what a valid value looks like has not been established about
            this one. A rule with no `message` reports `UNCHECKABLE_MESSAGE`.
        """
        msg = self.message or self._default_message()

        if self.type == "required":
            if value is None:
                return ValidationResult(False, msg)
            if isinstance(value, str) and not value.strip():
                return ValidationResult(False, msg)
            # Everything else is valid (non-empty string, number, date, etc.)
            return ValidationResult(True, "")

        # A rule other than `required` describes what a value must look like,
        # not that one must be present. An untouched optional field has nothing
        # to check, so it passes — otherwise leaving it blank would block a
        # submit with no way forward. Use `required` for presence, the same
        # contract `range` states below.
        if self.type in TEXT_RULES and _is_empty(value):
            return ValidationResult(True, "")

        if self.type == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", _as_text(value)):
                return ValidationResult(False, msg)
        elif self.type == "stringLength":
            min_len = self.params.get("min", 0)
            max_len = self.params.get("max", float("inf"))
            if not (min_len <= len(_as_text(value)) <= max_len):
                return ValidationResult(False, msg)
        elif self.type == "pattern":
            pattern = self.params.get("pattern", "")
            if not re.match(pattern, _as_text(value)):
                return ValidationResult(False, msg)
        elif self.type == "range":
            # Bounds on an ordered value (number/date/time). An empty field is
            # not out of range — use 'required' for presence.
            if _is_empty(value):
                return ValidationResult(True)
            lo = self.params.get("min")
            hi = self.params.get("max")
            try:
                if lo is not None and value < lo:
                    return ValidationResult(False, msg)
                if hi is not None and value > hi:
                    return ValidationResult(False, msg)
            except TypeError:
                # Incomparable types (e.g. a string bound against a number).
                return ValidationResult(False, msg)
        elif self.type == "compare":
            if value != self._read_other(self.params.get("other_field")):
                return ValidationResult(False, msg)
        elif self.type == "custom":
            func: Callable[[str], bool] = self.params.get("func")
            if func:
                try:
                    passed = func(value)
                except Exception as exc:
                    # A func that cannot judge this value has not produced a
                    # verdict, so report invalid -- the same answer the `range`
                    # branch above gives an incomparable pair. Letting it
                    # propagate leaves the field's validity stale instead: on an
                    # automatic trigger there is no caller to catch it, so the
                    # end user sees a field that quietly stopped validating.
                    # NOTE(#467): `Exception`, not `TypeError` -- `range` only
                    # compares, but a user func can raise anything. Narrowing
                    # this re-opens the defect for every other exception type.
                    # BaseException is deliberately not caught.
                    self._report_func_error(exc, value)
                    return ValidationResult(False, self._uncheckable_message())
                if not passed:
                    return ValidationResult(False, msg)

        return ValidationResult(True)

    def _uncheckable_message(self) -> str:
        """Return what to show the end user when the func raised.

        The rule's own `message` states a CONDITION -- "must be over 5" -- so
        returning it as the verdict asserts something about a value the predicate
        never managed to judge, and it can be plainly false: a field reading
        "must be over 5" while holding 6. But throwing it away leaves the user
        with nothing to act on, so it is demoted rather than discarded, from a
        judgment to an expectation.

        ⚠ Only an AUTHOR-SUPPLIED message is composed in. `self.message` is empty
        when the caller passed none, and `_default_message()` would then supply
        "Invalid value." -- composing that gives "Could not check this value
        (expected: Invalid value.)", which is nonsense. Read `self.message`, not
        the resolved `msg`.

        Returns:
            The end-user message for a predicate that raised.
        """
        if not self.message:
            return UNCHECKABLE_MESSAGE
        return f"Could not check this value (expected: {self.message.rstrip('.')})."

    def _report_func_error(self, exc: BaseException, value: object) -> None:
        """Report a `'custom'` func that raised, without ever raising itself.

        Absorbing the exception is what keeps the field's validity from going
        stale, but absorbing it silently would leave the author worse off than
        before the guard existed: on the automatic trigger Tk printed the
        traceback through `report_callback_exception`, and on the manual trigger
        the exception reached the caller. A func that raises is always a defect
        in the author's own code -- unlike `range`, whose silence is about the
        DATA -- so the framework must not be the thing that hides it.

        The first raise per rule writes one line naming the exception; the full
        traceback stays behind `BOOTSTACK_DEBUG`. Once per rule is required, not
        cosmetic: a rule with `trigger='always'` runs on every keystroke, and an
        unconditional print would flood the console as the user types.

        Args:
            exc: The exception the func raised.
            value: The value the func was given.
        """
        try:
            if not self._func_error_reported:
                self._func_error_reported = True
                print(
                    f"bootstack: a 'custom' validation rule's func raised "
                    f"{type(exc).__name__}: {exc} -- the value is reported "
                    f"invalid. Set BOOTSTACK_DEBUG=1 for the traceback.",
                    file=sys.stderr,
                )
            debug_log_exception(
                f"custom validation rule raised for value {value!r}"
            )
        except Exception:
            # A diagnostic must never become the failure it is reporting. The
            # value's own __repr__, or the exception's __str__, is user code and
            # can raise -- which would escape this guard and re-open #467.
            pass

    @staticmethod
    def _read_other(other: object) -> object:
        """Resolve the current value of a `'compare'` rule's `other_field`.

        Accepts a `Signal` or any zero-argument callable (called to read), a
        field wrapper exposing a `value` property, or a plain literal value.

        Args:
            other: The `other_field` parameter passed to the rule.

        Returns:
            The other field's current value, or `None` if `other` is `None`.
        """
        if other is None:
            return None
        if callable(other):
            return other()
        if hasattr(other, "value"):
            return other.value
        return other

    def _default_message(self) -> str:
        """Return a sensible default error message for this rule type."""
        if self.type == "required":
            return "This field is required."
        elif self.type == "email":
            return "Enter a valid email address."
        elif self.type == "stringLength":
            min_len = self.params.get("min", 0)
            max_len = self.params.get("max", None)
            if max_len is None or max_len == float("inf"):
                return f"Enter at least {min_len} characters."
            return f"Enter between {min_len} and {max_len} characters."
        elif self.type == "pattern":
            return "Value does not match the required pattern."
        elif self.type == "range":
            lo = self.params.get("min")
            hi = self.params.get("max")
            if lo is not None and hi is not None:
                return f"Enter a value between {lo} and {hi}."
            if lo is not None:
                return f"Enter a value of at least {lo}."
            if hi is not None:
                return f"Enter a value of at most {hi}."
            return "Value is out of range."
        elif self.type == "compare":
            return "Values do not match."
        elif self.type == "custom":
            return "Invalid value."
        return "Invalid input."

    def _default_trigger(self) -> RuleTriggerType:
        """Return the default trigger policy for this rule type."""
        if self.type == "required":
            return "always"
        elif self.type in {"stringLength", "compare", "range"}:
            return "blur"
        elif self.type in {"email", "pattern"}:
            return "always"
        elif self.type in {"custom"}:
            return "manual"
        return "blur"
