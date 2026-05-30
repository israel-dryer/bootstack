from __future__ import annotations

from typing import Any, Literal


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
        name: str | None = None,
        accent: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Insert a widget inside the field border.

        Args:
            widget: Widget type — `'button'`, `'label'`, or `'toggle'`.
            position: `'before'` (left of input) or `'after'` (right of input).
            name: Key to retrieve the addon later via `addons`. Auto-generated if omitted.
            accent: Accent token for the addon widget.
            **kwargs: Additional kwargs passed to the widget constructor
                (e.g. `icon=`, `command=`, `signal=`, `text=`).

        Returns:
            The created addon widget instance.
        """
        if widget not in self._ADDON_TYPES:
            raise ValueError(f"widget must be 'button', 'label', or 'toggle'; got {widget!r}")

        module_path, cls_name = self._ADDON_TYPES[widget].split("::")
        import importlib
        cls = getattr(importlib.import_module(module_path), cls_name)

        return self._internal.insert_addon(cls, position, name=name, accent=accent, **kwargs)

    @property
    def addons(self) -> dict[str, Any]:
        """Named addon widgets inserted via `insert_addon()`."""
        return self._internal.addons

    def add_validation_rule(self, rule_type: Any, **kwargs: Any) -> None:
        """Add a validation rule to the field.

        Args:
            rule_type: Rule identifier — e.g. `'required'`, `'min_length'`,
                `'max_length'`, `'pattern'`, `'email'`.
            **kwargs: Rule-specific options. `message=` overrides the default
                failure message for all rule types.
        """
        self._internal.add_validation_rule(rule_type, **kwargs)
