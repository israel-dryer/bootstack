from __future__ import annotations

from typing import overload, Any, Callable

from bootstack.widgets._impl.primitives.button import Button as _InternalButton
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events


class Button(PublicWidgetBase):
    """A clickable action trigger.

    Args:
        label: Button label text.
        on_click: Callback fired when the button is clicked.
        accent: Accent token, e.g. `'primary'`, `'danger'`.
        variant: Style variant, e.g. `'solid'`, `'outline'`.
        icon: Bootstrap Icons name.
        icon_only: If True, show only the icon (no label).
        disabled: If True, button is non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        label: str = "",
        *,
        on_click: Callable[[], Any] | None = None,
        accent: str | None = None,
        variant: str | None = None,
        icon: str | None = None,
        icon_only: bool = False,
        disabled: bool = False,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"text": label}
        if on_click is not None:
            internal_kwargs["command"] = on_click
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)

        self._internal = _InternalButton(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    @property
    def label(self) -> str:
        return str(self._internal.cget("text"))

    @label.setter
    def label(self, value: str) -> None:
        self._internal.configure(text=value)

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    def click(self) -> None:
        """Programmatically fire the button's command."""
        self._internal.invoke()

    def on_click(self, handler: Callable[[], Any]):
        """Register an additional click handler.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("click", lambda e: handler())


register_widget_events(Button, {})
