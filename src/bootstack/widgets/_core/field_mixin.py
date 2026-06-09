from __future__ import annotations

from typing import Any, Callable, Literal, TYPE_CHECKING

from bootstack.validation import RuleType
from bootstack.widgets.types import AccentToken

if TYPE_CHECKING:
    from bootstack.signals import Signal


class FieldAddonMixin:
    """Mixin that exposes `insert_addon` and `addons` on public field wrappers.

    Requires the inheriting class to have `self._internal` pointing to a
    `Field`-based composite that implements `insert_addon` / `addons`.
    """

    _ADDON_TYPES = {
        "button":  "bootstack.widgets._impl.primitives.button::Button",
        "label":   "bootstack.widgets._impl.primitives.label::Label",
        "toggle":  "bootstack.widgets._impl.primitives.checktoggle::CheckToggle",
    }

    def insert_addon(
        self,
        widget: Literal["button", "label", "toggle"],
        position: Literal["before", "after"],
        *,
        name: str | None = None,
        text: str | None = None,
        icon: str | None = None,
        accent: AccentToken | str | None = None,
        on_click: Callable[[], Any] | None = None,
        signal: "Signal | None" = None,
    ) -> Any:
        """Insert a small widget inside the field border, before or after the input.

        Use this for affordances such as a clear button, a search icon, a unit
        suffix label, or an on/off toggle.

        Args:
            widget: Addon type — `'button'` (clickable), `'label'` (static
                text or icon), or `'toggle'` (on/off control).
            position: `'before'` (left of the input) or `'after'` (right).
            name: Key to retrieve the addon later via `addons`. Auto-generated
                if omitted.
            text: Text shown on the addon. Applies to any addon type.
            icon: Bootstrap Icons name shown on the addon (e.g. `'search'`,
                `'x-lg'`). An icon-only addon is rendered when `icon` is given
                without `text`.
            accent: Accent token for the addon. Prefer an accent for a
                text-only button.
            on_click: Called with no arguments when a `'button'` or `'toggle'`
                addon is activated.
            signal: Reactive `Signal[bool]` bound to a `'toggle'` addon's
                on/off state.

        Returns:
            The created addon widget instance.
        """
        if widget not in self._ADDON_TYPES:
            raise ValueError(f"widget must be 'button', 'label', or 'toggle'; got {widget!r}")
        if on_click is not None and widget == "label":
            raise ValueError("on_click is not valid for a 'label' addon")
        if signal is not None and widget != "toggle":
            raise ValueError("signal is only valid for a 'toggle' addon")

        module_path, cls_name = self._ADDON_TYPES[widget].split("::")
        import importlib
        cls = getattr(importlib.import_module(module_path), cls_name)

        addon_kwargs: dict[str, Any] = {}
        if text is not None:
            addon_kwargs["text"] = text
        if icon is not None:
            addon_kwargs["icon"] = icon
        if on_click is not None:
            addon_kwargs["command"] = on_click
        if signal is not None:
            addon_kwargs["signal"] = signal

        return self._internal.insert_addon(cls, position, name=name, accent=accent, **addon_kwargs)

    @property
    def addons(self) -> dict[str, Any]:
        """Named addon widgets inserted via `insert_addon()`."""
        return self._internal.addons

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Any) -> None:
        """Add a validation rule to the field.

        Rules run automatically on blur or key events depending on the rule
        type, or manually via ``validate()``. Multiple rules can be added;
        they are evaluated in order and stop at the first failure.

        Args:
            rule_type: The kind of validation rule to apply.
            **kwargs: Rule-specific options:

                - ``message`` *(all rules)* — override the default error message.
                - ``trigger`` *(all rules)* — when to run: ``'always'`` (key and
                  blur), ``'key'``, ``'blur'``, or ``'manual'``. Each rule type
                  has its own sensible default (see the Validation reference).
                - ``min``, ``max`` *(stringLength)* — minimum/maximum character count.
                - ``pattern`` *(pattern)* — regex string the value must match.
                - ``other_field`` *(compare)* — field whose value must match.
                - ``func`` *(custom)* — callable ``(value: str) -> bool``.

        Example::

            field.add_validation_rule("required")
            field.add_validation_rule("stringLength", min=3, max=50)
            field.add_validation_rule("email", message="Enter a valid email.")
            field.add_validation_rule("custom", func=lambda v: v.isdigit())
        """
        self._internal.add_validation_rule(rule_type, **kwargs)
