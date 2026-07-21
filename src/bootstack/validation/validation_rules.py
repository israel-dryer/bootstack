import re
from typing import Callable

from bootstack.validation.types import RuleTriggerType, RuleType
from bootstack.validation.validation_result import ValidationResult


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

    def validate(self, value: str) -> ValidationResult:
        """Apply this rule to a value and return the result.

        Args:
            value: The string value to validate.

        Returns:
            A ValidationResult with `is_valid=True` on success or `is_valid=False`
            with an error message on failure.
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
            if func and not func(value):
                return ValidationResult(False, msg)

        return ValidationResult(True)

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
