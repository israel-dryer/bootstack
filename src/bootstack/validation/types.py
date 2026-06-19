from typing import Any, Callable, Literal, Optional, TypedDict

RuleType = Literal["required", "email", "pattern", "stringLength", "range", "custom", "compare"]
"""A built-in validation rule name."""

RuleTriggerType = Literal['key', 'blur', 'always', 'manual']


class ValidationOptions(TypedDict, total=False):
    pattern: str
    message: str
    min: Any
    max: Any
    trigger: Optional[Literal["key", "blur", "always", "manual"]]
    func: Callable[[str], bool]