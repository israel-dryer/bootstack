from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.composites.buttongroup import ButtonGroup as _InternalButtonGroup
from bootstack.widgets._core.base import PublicWidgetBase


class ButtonGroup(PublicWidgetBase):
    """A row (or column) of visually-connected buttons sharing accent and variant.

    Buttons are added via `add()`. The group propagates `accent`, `variant`,
    and `density` to every member automatically.

    Args:
        orient: `'horizontal'` (default) or `'vertical'`.
        accent: Accent token applied to all buttons.
        variant: Style variant — `'solid'` (default), `'outline'`, `'ghost'`.
        density: Widget density — `'default'` or `'compact'`.
        disabled: If True, all buttons are non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        orient: str = "horizontal",
        *,
        accent: str | None = None,
        variant: str = "solid",
        density: str = "default",
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "orient": orient,
            "variant": variant,
            "density": density,
        }
        if accent is not None:
            internal_kwargs["accent"] = accent
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalButtonGroup(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Item management -----

    def add(
        self,
        label: str = "",
        *,
        key: str | None = None,
        on_click: Callable[[], Any] | None = None,
        icon: str | None = None,
        disabled: bool = False,
        **kwargs: Any,
    ) -> str:
        """Add a button to the group.

        Args:
            label: Button label text.
            key: Unique string key. Auto-generated if omitted.
            on_click: Callback fired when the button is clicked.
            icon: Icon name shown on the button.
            disabled: If True, this button starts disabled.

        Returns:
            The key assigned to this button.
        """
        btn_kwargs: dict[str, Any] = {}
        if icon is not None:
            btn_kwargs["icon"] = icon
        if disabled:
            btn_kwargs["state"] = "disabled"
        btn_kwargs.update(kwargs)

        self._internal.add(label or None, key=key, command=on_click, **btn_kwargs)
        if key is None:
            key = f"widget_{self._internal._counter - 1}"
        return key

    def remove(self, key: str) -> None:
        """Remove the button identified by `key`.

        Args:
            key: Key returned by `add()`.
        """
        self._internal.remove(key)

    def update_item(self, key: str, **kwargs: Any) -> None:
        """Reconfigure a button after creation.

        Args:
            key: Key returned by `add()`.
            **kwargs: Options forwarded to the button's `configure()`.
        """
        self._internal.configure_item(key, **kwargs)

    # ----- Properties -----

    def item(self, key: str) -> Any:
        """Return the button item object for `key`.

        Args:
            key: Key returned by `add()`.
        """
        return self._internal.item(key)

    @property
    def items(self) -> tuple[Any, ...]:
        """All button items in insertion order."""
        return self._internal.items()

    @property
    def keys(self) -> tuple[str, ...]:
        """Keys of all buttons in insertion order."""
        return self._internal.keys()

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, v: bool) -> None:
        self._internal.configure(state="disabled" if v else "normal")

    @property
    def accent(self) -> str | None:
        return self._internal._accent

    @accent.setter
    def accent(self, v: str | None) -> None:
        self._internal.configure(accent=v)

    @property
    def variant(self) -> str:
        return self._internal._variant

    @variant.setter
    def variant(self, v: str) -> None:
        self._internal.configure(variant=v)