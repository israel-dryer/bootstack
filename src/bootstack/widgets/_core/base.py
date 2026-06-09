from __future__ import annotations

import tkinter
from typing import TYPE_CHECKING, Any, Callable, overload

from bootstack.widgets._core.context import current_container
from bootstack.widgets._core.events import resolve_event
from bootstack.events import Event, Subscription
from bootstack.errors import ParentResolutionError

if TYPE_CHECKING:
    from bootstack.scheduling import Schedule
    from bootstack.streams import Stream


def adapt_handler(handler: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Wrap a public handler so it receives a bootstack event, not a raw one.

    Data-carrying events (emitted with ``data=<payload>``) deliver the payload
    object directly — the handler argument *is* the payload. Native/context
    events carry no payload, so the raw toolkit event is curated into a clean
    :class:`~bootstack.events.Event` first.
    """

    def _wrapped(raw: Any) -> Any:
        payload = getattr(raw, "data", None)
        if payload is not None:
            return handler(payload)
        return handler(Event._from_tk(raw))

    return _wrapped


class PublicWidgetBase:
    """Base class for every public widget.

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
        from bootstack.widgets._core.container import (
            PACK_KEYS, GRID_KEYS, PLACE_KEYS, PLACE_TRIGGER_KEYS,
        )
        place_mode = any(k in kwargs for k in PLACE_TRIGGER_KEYS)
        if place_mode:
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

    @property
    def schedule(self) -> "Schedule":
        """Scheduler tied to this widget's lifetime.

        All jobs are automatically cancelled when the widget is destroyed.
        First access creates the `Schedule` instance; subsequent accesses
        return the same instance.

        Usage::

            self.schedule.delay(500, callback)
            self.schedule.every(1000, tick)
            job = self.schedule.idle(refresh)
            job.cancel()
        """
        if not hasattr(self, "_schedule"):
            from bootstack.scheduling import Schedule
            self._schedule = Schedule(self._internal)
        return self._schedule

    # ----- on() — overloaded -------------------------------------------------

    @overload
    def on(self, event: str) -> "Stream": ...
    @overload
    def on(self, event: str, handler: Callable[[Any], Any]) -> Subscription: ...

    def on(
        self,
        event: str,
        handler: Callable[[Any], Any] | None = None,
    ) -> "Stream | Subscription":
        """Bind `handler` to `event`, or return a composable `Stream`.

        With a handler — binds immediately and returns a `Subscription`::

            sub = widget.on("change", handler)
            sub.cancel()

        Without a handler — returns a `Stream` for operator chaining.
        The Tk binding is created lazily when `.listen()` is called::

            sub = widget.on("change").debounce(300).listen(handler)
            sub.cancel()

        Args:
            event: Event name (e.g. `"change"`, `"click"`).
            handler: Optional callback. If omitted, a `Stream` is returned.

        Returns:
            `Subscription` when a handler is provided; `Stream` otherwise.
        """
        sequence = resolve_event(self, str(event))

        if handler is not None:
            bind_id = self._internal.bind(sequence, adapt_handler(handler), add="+")
            return Subscription(self._internal, sequence, bind_id)

        # No handler — return a lazy Stream.
        from bootstack.streams import Stream

        widget = self._internal

        def _source(downstream: Callable[[Any], Any]) -> Subscription:
            bind_id = widget.bind(sequence, adapt_handler(downstream), add="+")
            return Subscription(widget, sequence, bind_id)

        return Stream(self._internal, _source=_source)

    def emit(self, event: str, *, data: Any = None) -> None:
        """Fire a named event on this widget, as if it produced the event itself.

        This is how a composite widget surfaces high-level activity to its
        listeners, and the generic counterpart to the `on_*()` shorthands for
        firing events that have no dedicated method.

        Args:
            event: The event name, unprefixed — the same name you pass to `on()`
                or an `on_<event>()` shorthand (e.g. `'change'`, `'select'`).
            data: The payload delivered to handlers. For a data-carrying event,
                pass the matching payload dataclass from `bootstack.events` — the
                same object an `on_<event>()` handler receives. Leave as None for
                native events (click, hover, focus, …), which carry no payload.

        Example:
            .. code-block:: python

               widget.emit("change", data=bs.events.ChangeEvent(value=new_value))
        """
        sequence = resolve_event(self, str(event))
        self._internal.event_generate(sequence, data=data)

    def __repr__(self) -> str:
        try:
            name = self._internal._w  # type: ignore[attr-defined]
        except AttributeError:
            name = "?"
        return f"<{type(self).__name__} {name}>"
