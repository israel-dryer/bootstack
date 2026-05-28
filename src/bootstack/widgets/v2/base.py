from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.v2.context import current_container
from bootstack.widgets.v2.events import resolve_event
from bootstack.widgets.v2.subscription import Subscription
from bootstack.widgets.v2.exceptions import ParentResolutionError


class PublicWidgetBase:
    """Base class for every public v2 widget.

    Subclasses must set `self._internal` before calling `_attach_to_parent`,
    and should use `_split_layout_kwargs` to strip layout kwargs before
    constructing the internal widget.
    """

    _auto_place: bool = True

    _internal: tkinter.Misc
    _parent: "PublicWidgetBase | None"

    @staticmethod
    def _resolve_parent(
        explicit_parent: "PublicWidgetBase | None",
    ) -> "PublicWidgetBase | None":
        if explicit_parent is not None:
            return explicit_parent
        return current_container()

    @staticmethod
    def _split_layout_kwargs(kwargs: dict) -> dict:
        """Pop and return layout kwargs from `kwargs`, mutating it in place."""
        # Lazy import breaks the container ↔ base circular dependency.
        from bootstack.widgets.v2.container import (
            PACK_KEYS, GRID_KEYS, PLACE_KEYS, PLACE_TRIGGER_KEYS,
        )
        place_mode = any(k in kwargs for k in PLACE_TRIGGER_KEYS)
        if place_mode:
            # `width`/`height`/`anchor` can collide with widget options; leave
            # them as widget kwargs unless a true trigger key is present too.
            layout_keys = (PLACE_KEYS - {"width", "height", "anchor"}) | PLACE_TRIGGER_KEYS
        else:
            layout_keys = PACK_KEYS | GRID_KEYS
        return {k: kwargs.pop(k) for k in list(kwargs) if k in layout_keys}

    def _attach_to_parent(self, layout_kw: dict) -> None:
        if not self._auto_place:
            return
        parent = self._parent
        if parent is None:
            return
        guide = getattr(parent, "guide_layout", None)
        if guide is None:
            raise ParentResolutionError(
                f"{type(parent).__name__} is not a container (no guide_layout); "
                f"cannot place {type(self).__name__} inside it."
            )
        guide(self, **layout_kw)

    @property
    def tk(self) -> tkinter.Misc:
        """Underlying tk/ttk widget. UNSUPPORTED — escape-hatch use only."""
        return self._internal

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Bind `handler` to `event` and return a `Subscription`."""
        sequence = resolve_event(self, str(event))
        bind_id = self._internal.bind(sequence, handler, add="+")
        return Subscription(self._internal, sequence, bind_id)

    def emit(self, event: str, *, data: dict | None = None) -> None:
        """Synthesize `event` on the underlying widget."""
        sequence = resolve_event(self, str(event))
        if data is not None:
            self._internal._bs_emit_data = data  # type: ignore[attr-defined]
        try:
            self._internal.event_generate(sequence)
        finally:
            if data is not None:
                try:
                    delattr(self._internal, "_bs_emit_data")
                except AttributeError:
                    pass

    def __repr__(self) -> str:
        try:
            name = self._internal._w  # type: ignore[attr-defined]
        except AttributeError:
            name = "?"
        return f"<{type(self).__name__} {name}>"
