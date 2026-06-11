from __future__ import annotations

from typing import Any


class SelectionGroupMixin:
    """Shared item-management surface for the option-group widgets.

    Mixed into `RadioGroup` and `ToggleGroup`, which both wrap an internal
    composite exposing `keys()`, `configure_item()`, and `remove()`. Each class
    keeps its own `add()` (the option semantics differ) and its own value /
    change surface; only the value-keyed item operations live here.
    """

    _internal: Any

    def remove(self, value: Any) -> None:
        """Remove the option identified by `value`.

        Args:
            value: The value the option was added with.

        Raises:
            KeyError: If no option with that value exists.
        """
        self._internal.remove(value)

    def configure_item(
        self,
        value: Any,
        *,
        label: str | None = None,
        disabled: bool | None = None,
    ) -> None:
        """Update a single option in place, without rebuilding the group.

        Args:
            value: The option to update (the value it was added with).
            label: New display text, when given.
            disabled: When given, disable (`True`) or re-enable (`False`) just
                this option. A later group-level `disabled` change resets every
                option's state, so apply per-option states after it.

        Raises:
            KeyError: If no option with that value exists.
        """
        if label is not None:
            self._internal.configure_item(value, text=label)
        if disabled is not None:
            self._internal.configure_item(value, state="disabled" if disabled else "normal")

    def __len__(self) -> int:
        """The number of options in the group."""
        return len(self._internal.keys())

    def __contains__(self, value: Any) -> bool:
        """Whether an option with the given `value` is in the group."""
        return value in self._internal.keys()