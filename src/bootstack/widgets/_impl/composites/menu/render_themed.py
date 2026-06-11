"""Windows/Linux renderer — a themed in-window menu-bar strip.

Builds a horizontal strip of trigger buttons (one per `MenuGroup`) from a
`MenuModel`. Each trigger is a `DropdownButton` whose popdown is the themed
`_ToplevelContextMenu` backend, so theme tokens, density, and icons all apply.
macOS uses the native renderer instead (`render_native`).
"""
from __future__ import annotations

from tkinter import StringVar
from typing import Any

from bootstack.widgets._impl.composites.contextmenu import ContextMenuItem
from bootstack.widgets._impl.composites.dropdownbutton import DropdownButton
from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._impl.composites.menu.model import MenuItem, MenuModel
from bootstack.widgets.types import Master, WidgetDensity


class ThemedMenuBar(PackFrame):
    """Themed menu-bar strip (Windows/Linux) rendered from a `MenuModel`.

    The strip is a horizontal row of dropdown triggers. Call `rebuild()` to
    re-render after the model changes.
    """

    def __init__(
        self,
        master: Master = None,
        model: MenuModel | None = None,
        *,
        density: WidgetDensity = "compact",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("surface", "chrome")
        super().__init__(master, direction="horizontal", fill_items="y", **kwargs)
        self._model = model if model is not None else MenuModel()
        self._density = density
        self._triggers: list[DropdownButton] = []
        # One shared Tk variable per radio group name so radio items in the
        # same group are mutually exclusive.
        self._radio_vars: dict[str, StringVar] = {}
        self.rebuild()

    @property
    def model(self) -> MenuModel:
        """The menu model this strip renders."""
        return self._model

    def set_model(self, model: MenuModel) -> None:
        """Swap in a new model and re-render."""
        self._model = model
        self.rebuild()

    def rebuild(self) -> None:
        """Tear down and re-render every trigger from the current model."""
        for trigger in self._triggers:
            try:
                trigger.destroy()
            except Exception:
                pass
        self._triggers = []
        self._radio_vars = {}

        for group in self._model:
            items = [self._to_context_item(item) for item in group.items]
            trigger = DropdownButton(
                self,
                text=group.text,
                items=items,
                variant="menubar-item",
                show_dropdown_button=False,
                density=self._density,
            )
            trigger.pack(side="left")
            self._triggers.append(trigger)

    def _to_context_item(self, item: MenuItem) -> ContextMenuItem:
        """Translate a model `MenuItem` into a `ContextMenuItem`.

        Maps the public type names to the ContextMenu backend's Tk-derived
        names (`action`->`command`, `check`->`checkbutton`,
        `radio`->`radiobutton`). The raw `shortcut` is forwarded for display
        only — actual key binding is owned by `MenuModel.bind_shortcuts`.
        """
        if item.type == "separator":
            return ContextMenuItem("separator", key=item.key)

        if item.type == "check":
            return ContextMenuItem(
                "checkbutton",
                text=item.text,
                value=item.checked,
                command=item.on_click,
                key=item.key,
            )

        if item.type == "radio":
            var = self._radio_vars.setdefault(item.group or "", StringVar())
            return ContextMenuItem(
                "radiobutton",
                text=item.text,
                value=item.value,
                variable=var,
                command=item.on_click,
                disabled=item.disabled,
                key=item.key,
            )

        # action
        kwargs: dict[str, Any] = {
            "text": item.text,
            "command": item.on_click,
            "disabled": item.disabled,
            "key": item.key,
        }
        if item.icon:
            kwargs["icon"] = item.icon
        if item.shortcut:
            kwargs["shortcut"] = item.shortcut
        return ContextMenuItem("command", **kwargs)