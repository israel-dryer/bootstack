from __future__ import annotations

from typing import overload, Any, Callable, Literal

from bootstack.widgets._impl.primitives.treeview import TreeView as _InternalTreeView
from bootstack.widgets._core.base import PublicWidgetBase, adapt_handler
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream


_TREE_EVENTS: dict[str, str] = {
    "select":   "<<TreeviewSelect>>",
    "open":     "<<TreeviewOpen>>",
    "close":    "<<TreeviewClose>>",
}

register_widget_events(_InternalTreeView, _TREE_EVENTS)


class Tree(PublicWidgetBase):
    """A hierarchical tree/table widget backed by `ttk.Treeview`.

    Displays data in a tree structure (with optional columns). Rows are
    called *items*; each item has a unique IID, optional text, optional
    icon, optional column values, and optional child items.

    Args:
        columns: Sequence of column IDs to define. Omit for tree-only mode.
        show: Which parts to render — `'tree headings'` (default), `'tree'`,
            or `'headings'`.
        height: Number of visible rows.
        selection_mode: `'extended'` (default, multi-select), `'browse'`
            (single), or `'none'`.
        show_border: Draw a border around the widget.
        density: Visual density — `'default'` or `'compact'`.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        columns: list[str] | None = None,
        show: str = "tree headings",
        height: int | None = None,
        selection_mode: Literal["extended", "browse", "none"] = "extended",
        show_border: bool = False,
        density: str | None = None,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "show": show,
            "selectmode": selection_mode,
            "show_border": show_border,
        }
        if columns is not None:
            internal_kwargs["columns"] = columns
        if height is not None:
            internal_kwargs["height"] = height
        if density is not None:
            internal_kwargs["density"] = density
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalTreeView(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    @overload
    def on(self, event: str) -> Stream: ...
    @overload
    def on(self, event: str, handler: Callable) -> Subscription: ...
    def on(self, event: str, handler: Callable | None = None) -> Stream | Subscription:
        from bootstack.widgets._core.events import resolve_event
        sequence = resolve_event(self._internal, str(event))
        if handler is None:
            def _source(h):
                _bid = self._internal.bind(sequence, adapt_handler(h), add="+")
                return Subscription(self._internal, sequence, _bid)
            return Stream(self._internal, _source=_source)
        bind_id = self._internal.bind(sequence, adapt_handler(handler), add="+")
        return Subscription(self._internal, sequence, bind_id)

    # ----- Item management -----

    def insert(
        self,
        parent: str = "",
        index: str | int = "end",
        *,
        iid: str | None = None,
        text: str = "",
        values: tuple | list | None = None,
        open: bool = False,
        image: Any = None,
        tags: str | tuple | None = None,
    ) -> str:
        """Insert a new item into the tree.

        Args:
            parent: IID of the parent item, or `''` for a root item.
            index: Position among siblings — `'end'` (default) or an integer.
            iid: Explicit IID. Auto-generated if omitted.
            text: Label text shown in the tree column.
            values: Sequence of column values (in column-definition order).
            open: Whether the item is expanded initially.
            image: Icon image.
            tags: Tag or tuple of tags.

        Returns:
            The IID assigned to the new item.
        """
        kw: dict[str, Any] = {"text": text, "open": open}
        if iid is not None:
            kw["iid"] = iid
        if values is not None:
            kw["values"] = values
        if image is not None:
            kw["image"] = image
        if tags is not None:
            kw["tags"] = tags
        return self._internal.insert(parent, index, **kw)

    def delete(self, *items: str) -> None:
        """Delete one or more items (and their descendants) by IID.

        Args:
            *items: IIDs to delete.
        """
        self._internal.delete(*items)

    def detach(self, *items: str) -> None:
        """Remove items from the display without deleting them.

        They can be re-attached via `move()`.

        Args:
            *items: IIDs to detach.
        """
        self._internal.detach(*items)

    def move(self, item: str, parent: str, index: str | int) -> None:
        """Move an item to a new parent/position.

        Args:
            item: IID of the item to move.
            parent: IID of the new parent, or `''` for root level.
            index: Position among siblings.
        """
        self._internal.move(item, parent, index)

    def clear(self) -> None:
        """Delete all items."""
        self._internal.delete(*self._internal.get_children())

    # ----- Item access -----

    def item(self, item: str, **options: Any) -> Any:
        """Get or set options on an item.

        Called with no extra kwargs, returns a dict of the item's current options.

        Args:
            item: IID.
            **options: Options to set (`text`, `values`, `open`, `image`, `tags`).
        """
        return self._internal.item(item, **options)

    def set(self, item: str, column: str | None = None, value: Any = None) -> Any:
        """Get or set a column value for an item.

        Args:
            item: IID.
            column: Column ID. If omitted, returns all column values as a dict.
            value: New value to set. If omitted, returns the current value.
        """
        if column is None:
            return self._internal.set(item)
        if value is None:
            return self._internal.set(item, column)
        return self._internal.set(item, column, value)

    def get_children(self, item: str = "") -> tuple[str, ...]:
        """Return the IIDs of an item's direct children.

        Args:
            item: IID of the parent, or `''` for root items.
        """
        return self._internal.get_children(item)

    def exists(self, item: str) -> bool:
        """Return `True` if an item with the given IID exists.

        Args:
            item: IID to check.
        """
        return self._internal.exists(item)

    def see(self, item: str) -> None:
        """Scroll the tree so `item` is visible.

        Args:
            item: IID to scroll to.
        """
        self._internal.see(item)

    def focus(self, item: str | None = None) -> str:
        """Get or set the focused item.

        Args:
            item: IID to focus. Omit to return the currently focused IID.

        Returns:
            Currently focused IID when called without an argument.
        """
        if item is None:
            return self._internal.focus()
        return self._internal.focus(item)

    # ----- Column / heading config -----

    def column(self, column: str, **options: Any) -> Any:
        """Configure a column.

        Args:
            column: Column ID.
            **options: Column options — `width`, `minwidth`, `anchor`,
                `stretch`, `id`.
        """
        return self._internal.column(column, **options)

    def heading(self, column: str, **options: Any) -> Any:
        """Configure a column heading.

        Args:
            column: Column ID.
            **options: Heading options — `text`, `anchor`, `image`, `command`.
        """
        return self._internal.heading(column, **options)

    # ----- Selection -----

    def selection(self) -> tuple[str, ...]:
        """Return the IIDs of all selected items."""
        return self._internal.selection()

    def selection_set(self, *items: str) -> None:
        """Set the selection to exactly these items.

        Args:
            *items: IIDs to select (replaces any existing selection).
        """
        self._internal.selection_set(*items)

    def selection_add(self, *items: str) -> None:
        """Add items to the current selection.

        Args:
            *items: IIDs to add.
        """
        self._internal.selection_add(*items)

    def selection_remove(self, *items: str) -> None:
        """Remove items from the current selection.

        Args:
            *items: IIDs to remove.
        """
        self._internal.selection_remove(*items)

    def selection_clear(self) -> None:
        """Deselect all items."""
        self._internal.selection_set()

    # ----- Expand / collapse -----

    def expand(self, item: str) -> None:
        """Expand an item to show its children.

        Args:
            item: IID to expand.
        """
        self._internal.item(item, open=True)

    def collapse(self, item: str) -> None:
        """Collapse an item to hide its children.

        Args:
            item: IID to collapse.
        """
        self._internal.item(item, open=False)

    # ----- Events -----

    def on_select(self, callback: Callable) -> str:
        """Register a callback for `<<TreeviewSelect>>` events.

        Args:
            callback: Called when the selection changes.

        Returns:
            Bind ID — pass to `off_select()` to unsubscribe.
        """
        return self._internal.bind("<<TreeviewSelect>>", callback, add="+")

    def off_select(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TreeviewSelect>>`.

        Args:
            bind_id: ID returned by `on_select()`. If `None`, removes all.
        """
        self._internal.unbind("<<TreeviewSelect>>", bind_id)

    def on_open(self, callback: Callable) -> str:
        """Register a callback for `<<TreeviewOpen>>` events (item expanded).

        Args:
            callback: Called when an item is opened/expanded.

        Returns:
            Bind ID — pass to `off_open()` to unsubscribe.
        """
        return self._internal.bind("<<TreeviewOpen>>", callback, add="+")

    def off_open(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TreeviewOpen>>`.

        Args:
            bind_id: ID returned by `on_open()`. If `None`, removes all.
        """
        self._internal.unbind("<<TreeviewOpen>>", bind_id)

    def on_close(self, callback: Callable) -> str:
        """Register a callback for `<<TreeviewClose>>` events (item collapsed).

        Args:
            callback: Called when an item is closed/collapsed.

        Returns:
            Bind ID — pass to `off_close()` to unsubscribe.
        """
        return self._internal.bind("<<TreeviewClose>>", callback, add="+")

    def off_close(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<TreeviewClose>>`.

        Args:
            bind_id: ID returned by `on_close()`. If `None`, removes all.
        """
        self._internal.unbind("<<TreeviewClose>>", bind_id)
