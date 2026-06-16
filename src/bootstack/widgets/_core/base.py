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
    _placement: Any  # container.Placement — set when first placed in a layout

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
            PACK_KEYS, GRID_KEYS, PLACE_KEYS, PLACE_TRIGGER_KEYS, FLEX_CHILD_KEYS,
        )
        place_mode = any(k in kwargs for k in PLACE_TRIGGER_KEYS)
        if place_mode:
            layout_keys = (PLACE_KEYS - {"width", "height", "anchor"}) | PLACE_TRIGGER_KEYS
        else:
            layout_keys = PACK_KEYS | GRID_KEYS | FLEX_CHILD_KEYS
        layout = {k: kwargs.pop(k) for k in list(kwargs) if k in layout_keys}
        # `attached` is geometry-manager-agnostic — capture it in every mode.
        if "attached" in kwargs:
            layout["attached"] = kwargs.pop("attached")
        return layout

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

    # ----- Lifecycle --------------------------------------------------------

    def destroy(self) -> None:
        """Destroy the widget and release the resources it holds.

        Removes the widget from its parent, destroys its children, and cancels
        any pending or repeating jobs on its `schedule`. After this the widget
        must not be used again. Destroying a container destroys everything
        inside it.
        """
        self._internal.destroy()

    @property
    def is_attached(self) -> bool:
        """Whether the widget is currently placed in its layout.

        `True` while the widget occupies space in its parent; `False` after
        `detach` (or before it has ever been placed). A detached widget keeps
        its state and can be returned to the layout with `attach`.
        """
        try:
            return bool(self._internal.winfo_manager())
        except tkinter.TclError:
            return False

    def detach(self) -> None:
        """Remove the widget from its layout without destroying it.

        The widget stops occupying space but keeps its state, children, and
        event bindings, ready to be returned with `attach`. The current
        position is snapshotted so a plain `attach()` restores it exactly —
        for stacked siblings this is the index among the *currently attached*
        siblings, so detaching other siblings first shifts that index.

        Calling `detach` on a widget that is already detached, or one that was
        never placed in a layout, does nothing. Fires `on_detach`.
        """
        placement = getattr(self, "_placement", None)
        if placement is None or not self.is_attached:
            return
        if placement.method == "flex":
            # The FlexFrame's managed list IS the attached-sibling order, so the
            # current managed index is the slot a plain attach() should restore.
            idx = placement.master.index_of(self._internal)
            placement.index = idx if idx >= 0 else None
            placement.master.remove_child(self._internal)
        elif placement.method == "pack":
            slaves = list(placement.master.pack_slaves())
            try:
                placement.index = slaves.index(self._internal)
            except ValueError:
                placement.index = None
            self._internal.pack_forget()
        elif placement.method == "grid":
            # grid_forget (not grid_remove): the "remembered" state left by
            # grid_remove rejects an explicit re-grid; we reconstruct fully
            # from the stored cell options instead.
            self._internal.grid_forget()
        else:
            self._internal.place_forget()

    def attach(self, **kwargs: Any) -> None:
        """Return a detached widget to its layout, optionally moving it.

        With no arguments, restores the widget to exactly where `detach` took
        it from. Any layout kwargs accepted by the original placement (e.g.
        `fill`, `expand`, `anchor`, `sticky`, `margin`) override the stored
        options. For stacked widgets, `index=` sets the position among the
        currently attached siblings (or pass an explicit `before=`/`after=`
        sibling); without one, the snapshotted position is used.

        Calling `attach` on a widget that is already attached moves it (the
        kwargs are re-applied). Fires `on_attach`.

        Args:
            **kwargs: Layout placement options to override for this placement.

        Raises:
            ParentResolutionError: If the widget was never placed in a layout.
        """
        from bootstack.widgets._core.container import (
            PACK_KEYS, GRID_KEYS, PLACE_KEYS, FLEX_CHILD_KEYS,
            normalize_fill, _expand_margin, _flex_child_opts, _reject_legacy_child_kwargs,
        )

        placement = getattr(self, "_placement", None)
        if placement is None:
            raise ParentResolutionError(
                f"{type(self).__name__} was never placed in a layout; "
                f"nothing to attach()."
            )
        # Re-applying to an attached widget is a move: clear it first so the
        # placement (and any index math) starts from a clean slate.
        if self.is_attached:
            self.detach()

        master = placement.master
        options = dict(placement.options)

        if placement.method == "flex":
            index = kwargs.pop("index", placement.index)
            if kwargs:
                _reject_legacy_child_kwargs(kwargs, type(self).__name__)
                _expand_margin(kwargs)
                options.update(_flex_child_opts(self, kwargs))
            master.add_child(self._internal, options, index=index)
            placement.options = options
            return

        if kwargs:
            if "fill" in kwargs:
                kwargs["fill"] = normalize_fill(kwargs["fill"])
            _expand_margin(kwargs)

        if placement.method == "pack":
            order = {k: kwargs.pop(k) for k in ("index", "before", "after") if k in kwargs}
            options.update({k: v for k, v in kwargs.items() if k in PACK_KEYS})
            if not order and placement.index is not None:
                order["index"] = placement.index
            order_kw = resolve_pack_order(order, master)
            self._internal.pack(in_=master, **options, **order_kw)
        elif placement.method == "grid":
            options.update({k: v for k, v in kwargs.items() if k in GRID_KEYS})
            self._internal.grid(in_=master, **options)
        else:
            options.update({k: v for k, v in kwargs.items() if k in PLACE_KEYS})
            self._internal.place(in_=master, **options)
        placement.options = options

    @overload
    def on_destroy(self) -> "Stream": ...
    @overload
    def on_destroy(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_destroy(
        self,
        handler: Callable[[Event], Any] | None = None,
    ) -> "Stream | Subscription":
        """Register a callback fired when the widget is destroyed.

        Fires once, as the widget is torn down — the place to release resources
        the widget owns that aren't cleaned up automatically (file handles,
        observers, external subscriptions). The handler receives a curated
        :class:`~bootstack.events.Event`.

        Args:
            handler: Called as the widget is destroyed. Omit to get a composable
                :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("destroy", handler)

    @overload
    def on_attach(self) -> "Stream": ...
    @overload
    def on_attach(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_attach(
        self,
        handler: Callable[[Event], Any] | None = None,
    ) -> "Stream | Subscription":
        """Register a callback fired when the widget enters the layout.

        Fires each time the widget becomes visible in its parent — on initial
        placement and on every `attach`. Pair it with `on_detach` to keep
        per-visibility resources (timers, observers) tied to the widget's
        presence on screen. The handler receives a curated
        :class:`~bootstack.events.Event`.

        Args:
            handler: Called when the widget is attached. Omit to get a
                composable :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("attach", handler)

    @overload
    def on_detach(self) -> "Stream": ...
    @overload
    def on_detach(self, handler: Callable[[Event], Any]) -> Subscription: ...
    def on_detach(
        self,
        handler: Callable[[Event], Any] | None = None,
    ) -> "Stream | Subscription":
        """Register a callback fired when the widget leaves the layout.

        Fires each time the widget stops occupying space in its parent — on
        `detach` and when an ancestor hides it. Pair it with `on_attach` to
        release per-visibility resources. The handler receives a curated
        :class:`~bootstack.events.Event`.

        Args:
            handler: Called when the widget is detached. Omit to get a
                composable :class:`~bootstack.streams.Stream`.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a handler
            is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("detach", handler)

    def __repr__(self) -> str:
        try:
            name = self._internal._w  # type: ignore[attr-defined]
        except AttributeError:
            name = "?"
        return f"<{type(self).__name__} {name}>"
