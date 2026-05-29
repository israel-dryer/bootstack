from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.composites.expander import Expander as _InternalExpander
from bootstack.widgets.composites.accordion import Accordion as _InternalAccordion
from bootstack.widgets.public.container import PublicContainer, PACK_KEYS
from bootstack.widgets.public.base import PublicWidgetBase
from bootstack.widgets.public.context import push_container, pop_container
from bootstack.widgets.public.events import register_widget_events
from bootstack.widgets.public.subscription import Subscription

_EXPANDER_EVENTS: dict[str, str] = {
    "expand":   "<<Toggle>>",
    "collapse":  "<<Toggle>>",
    "toggle":    "<<Toggle>>",
}


class Expander(PublicContainer):
    """A collapsible container with a clickable header.

    Children placed inside the context block go into the expandable body.

    Args:
        title: Header text.
        expanded: If True (default), body is visible on creation.
        collapsible: If False, the header cannot be clicked to collapse.
        icon: Icon displayed in the header (left of title).
        accent: Accent token for header styling.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        title: str = "",
        *,
        expanded: bool = True,
        collapsible: bool = True,
        icon: str | None = None,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "title": title,
            "expanded": expanded,
            "collapsible": collapsible,
        }
        if icon is not None:
            internal_kwargs["icon"] = icon
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalExpander(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    def _child_master(self) -> tkinter.Misc:
        return self._internal._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        return ("pack", {k: v for k, v in layout_kw.items() if k in PACK_KEYS})

    # ----- Properties -----

    @property
    def expanded(self) -> bool:
        return self._internal._expanded

    # ----- Methods -----

    def expand(self) -> None:
        """Expand the body."""
        self._internal.expand()

    def collapse(self) -> None:
        """Collapse the body."""
        self._internal.collapse()

    def toggle(self) -> None:
        """Toggle between expanded and collapsed."""
        self._internal.toggle()

    # ----- Event shorthands -----

    def on_toggle(self, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Register a callback fired when the expander is expanded or collapsed.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("toggle", handler)


register_widget_events(Expander, _EXPANDER_EVENTS)


# ---------------------------------------------------------------------------
# _AccordionSection — lightweight context-manager wrapper returned by
# Accordion.add(). Not part of the public API directly.
# ---------------------------------------------------------------------------

class _AccordionSection:
    """Context-manager wrapper around an Accordion section body."""

    def __init__(self, internal_expander: _InternalExpander) -> None:
        self._expander = internal_expander

    def _child_master(self) -> tkinter.Misc:
        return self._expander._content_frame

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        child._internal.pack(in_=self._child_master(), **options)

    def __enter__(self) -> "_AccordionSection":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)


class Accordion(PublicWidgetBase):
    """A list of collapsible sections, optionally limited to one open at a time.

    Args:
        allow_multiple: If True, multiple sections can be expanded simultaneously.
            Default `False` (only one section open at a time).
        allow_collapse_all: If True, all sections can be collapsed. Default `True`.
        accent: Accent token for section headers.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        allow_multiple: bool = False,
        allow_collapse_all: bool = True,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "allow_multiple": allow_multiple,
            "allow_collapse_all": allow_collapse_all,
        }
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalAccordion(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    def add(
        self,
        title: str,
        *,
        expanded: bool | None = None,
        icon: str | None = None,
    ) -> _AccordionSection:
        """Add a section and return a context manager for placing its children.

        Usage::

            with acc.add("Section title") as section:
                Label("Content goes here")

        Returns:
            `_AccordionSection` — use as a context manager to place children.
        """
        kwargs: dict[str, Any] = {}
        if expanded is not None:
            kwargs["expanded"] = expanded
        if icon is not None:
            kwargs["icon"] = icon
        internal_exp = self._internal.add(title=title, **kwargs)
        return _AccordionSection(internal_exp)
