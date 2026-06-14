from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.primitives.scrollbar import Scrollbar as _InternalScrollbar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets.types import AccentToken, Orient, ScrollbarVariant


class Scrollbar(PublicWidgetBase):
    """A themed scrollbar — horizontal or vertical.

    Most users will never instantiate `Scrollbar` directly; scrollable
    containers wire scrollbars automatically. Use this when you need an
    explicit, manually managed scrollbar.

    Args:
        orient: `'vertical'` (default) or `'horizontal'`.
        on_scroll: Callback invoked on scroll actions. Receives the scroll
            arguments — `(fraction,)` for a move, or `(first, last)` for a drag.
        accent: Accent token for styling.
        variant: Scrollbar style — `'default'` (standard rounded bar) or
            `'thin'` (slim square bar).
        parent: Override the context-stack parent.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        orient: Orient = "vertical",
        *,
        on_scroll: Callable | None = None,
        accent: AccentToken | str | None = None,
        variant: ScrollbarVariant = "default",
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"orient": orient}
        if on_scroll is not None:
            internal_kwargs["command"] = on_scroll
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        # **kwargs is layout-only (split out above) — not forwarded to the internal.

        self._internal = _InternalScrollbar(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    @property
    def position(self) -> tuple[float, float]:
        """Current scroll position as a `(first, last)` fraction pair."""
        return self._internal.get()

    @position.setter
    def position(self, value: tuple[float, float]) -> None:
        self._internal.set(*value)