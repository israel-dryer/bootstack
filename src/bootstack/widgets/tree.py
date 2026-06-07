from __future__ import annotations

from typing import Any, Callable, Literal, overload

from bootstack.widgets._impl.composites.tree.treeview import TreeView as _InternalTreeView
from bootstack.widgets._impl.composites.tree.treenode import TreeNode
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, WidgetDensity

__all__ = ["Tree", "TreeNode"]


class Tree(PublicWidgetBase):
    """A hierarchical tree for navigation and selection.

    Tree displays nested data as expandable rows. It is a *hierarchy-first*
    widget — reach for it when the structure is the point (file trees, outlines,
    settings navigation, grouped pickers). For flat records with columns,
    sorting, filtering, and paging, use `DataTable` instead.

    Nodes are object handles: `add()` returns a `TreeNode` that you hold and
    pass back to `expand()`, `select()`, `remove()`, and so on — there are no
    string ids. Each node carries a `label`, optional `icon`, `description`
    (dimmed, secondary text), and `badge`, plus an open-ended `data` bag for
    your own attributes.

    Args:
        nodes: Declarative initial tree — a list of node specs, where each spec
            is a label string or a dict like
            ``{"label": "src", "icon": "folder", "children": [...]}``. Anything
            not a recognized display key becomes that node's `data`.
        selection_mode: ``'single'`` (default) — one highlighted node;
            ``'multi'`` — click-to-toggle a set; ``'none'`` — no highlight
            selection (navigation/display only).
        show_selection_controls: If ``True``, show a per-node selection control
            (a checkbox in ``multi`` mode, a radio in ``single`` mode) as the
            visible affordance for selection — mirroring ListView and DataTable.
            While shown, the row highlight wash is suppressed (the control is the
            indicator).
        select_on_click: If ``True`` (default), clicking a row selects it. Set
            ``False`` with ``show_selection_controls=True`` so that only the
            control selects and a row click just focuses (e.g. to drive
            ``on_activate`` for opening, VS Code style).
        indent: Horizontal indent per depth level, in pixels. Defaults to 16.
        striped: If ``True``, alternate the row background color.
        show_scrollbar: If ``True`` (default), show the vertical scrollbar.
            Mousewheel scrolling works regardless.
        height: Fixed height in pixels. When set, the tree maintains this
            height regardless of its content (so it can scroll without the
            parent layout providing a vertical constraint).
        density: Row height — ``'default'`` (default) or ``'compact'``.
        accent: Color intent token for the selection highlight. One of
            ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
            ``'warning'``, ``'danger'``.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        *,
        nodes: list | None = None,
        selection_mode: Literal["none", "single", "multi"] = "single",
        show_selection_controls: bool = False,
        select_on_click: bool = True,
        indent: int = 16,
        striped: bool = False,
        show_scrollbar: bool = True,
        height: int | None = None,
        density: WidgetDensity = "default",
        accent: AccentToken | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "selection_mode": selection_mode,
            "show_selection_controls": show_selection_controls,
            "select_on_click": select_on_click,
            "indent": indent,
            "striped": striped,
            "scrollbar_visibility": "always" if show_scrollbar else "never",
            "density": density,
        }
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        if height is not None and "fill" not in layout_kw:
            layout_kw["fill"] = "x"

        self._internal = _InternalTreeView(tk_master, **internal_kwargs)
        # Stop the row pool from feeding back into the layout (see ListView).
        self._internal.pack_propagate(False)
        self._attach_to_parent(layout_kw)

        if height is not None:
            self._internal.configure(height=height)
        if nodes:
            self._internal.load(nodes)

    # ----- building -----

    def add(
        self,
        label: str = "",
        *,
        parent: TreeNode | None = None,
        icon: str | None = None,
        open_icon: str | None = None,
        closed_icon: str | None = None,
        description: str | None = None,
        badge: str | None = None,
        expanded: bool = False,
        children: list | None = None,
        loader: Callable[[TreeNode], Any] | None = None,
        data: dict | None = None,
        **extra: Any,
    ) -> TreeNode:
        """Add a node and return its `TreeNode` handle.

        Args:
            label: The node's display label.
            parent: Parent node, or ``None`` for a root node.
            icon: Bootstrap icon name shown before the label.
            open_icon: Icon used when the node is expanded (overrides `icon`).
            closed_icon: Icon used when the node is collapsed (overrides `icon`).
            description: Dimmed secondary text shown after the label.
            badge: Short label shown at the right edge of the row.
            expanded: Whether the node starts expanded.
            children: Optional child specs (same format as `nodes=`).
            loader: Callable invoked on first expand to fetch children lazily.
                Receives the node; returns an iterable of child specs.
            data: Initial data bag for the node.
            **extra: Extra keywords folded into the node's `data`.
        """
        return self._internal.add(
            label, parent=parent, icon=icon, open_icon=open_icon,
            closed_icon=closed_icon, description=description, badge=badge,
            expanded=expanded, children=children, loader=loader, data=data,
            **extra,
        )

    def insert(self, index: int, label: str = "", *, parent: TreeNode | None = None,
               **kwargs: Any) -> TreeNode:
        """Add a node at a specific position among its siblings.

        Args:
            index: Zero-based position among siblings.
            label: The node's display label.
            parent: Parent node, or ``None`` for a root node.
            **kwargs: Same as `add()`.
        """
        return self._internal.add(label, parent=parent, index=index, **kwargs)

    def remove(self, node: TreeNode) -> None:
        """Remove a node (and its descendants).

        Args:
            node: The node to remove.
        """
        self._internal.remove(node)

    def move(self, node: TreeNode, parent: TreeNode | None = None,
             index: int | str = "end") -> None:
        """Move a node to a new parent and/or position.

        Args:
            node: The node to move.
            parent: New parent, or ``None`` for the root level.
            index: Position among the new siblings — ``'end'`` or an integer.
        """
        self._internal.move(node, parent, index)

    def clear(self) -> None:
        """Remove all nodes."""
        self._internal.clear()

    # ----- expansion -----

    def expand(self, node: TreeNode) -> None:
        """Expand a node to reveal its children."""
        self._internal.expand(node)

    def collapse(self, node: TreeNode) -> None:
        """Collapse a node to hide its children."""
        self._internal.collapse(node)

    def expand_all(self) -> None:
        """Expand every node (loading lazy children as needed)."""
        self._internal.expand_all()

    def collapse_all(self) -> None:
        """Collapse every node."""
        self._internal.collapse_all()

    def reveal(self, node: TreeNode) -> None:
        """Expand ancestors and scroll so `node` is visible."""
        self._internal.reveal(node)

    def reload_children(self, node: TreeNode) -> None:
        """Refresh a lazy node's children — drop them and re-fetch via its
        `loader`. If `node` is expanded the children reload immediately;
        otherwise they reload on the next expand. A no-op for non-lazy nodes.

        Args:
            node: The lazy node (created with `loader=`) to refresh.
        """
        self._internal.reload_children(node)

    # ----- selection -----

    @property
    def selected_nodes(self) -> list[TreeNode]:
        """The currently selected nodes, in tree order."""
        return self._internal.get_selected()

    def select(self, node: TreeNode) -> None:
        """Select a node (replaces in single mode, adds in multi)."""
        self._internal.select(node)

    def deselect(self, node: TreeNode) -> None:
        """Remove a node from the selection."""
        self._internal.deselect(node)

    def select_all(self) -> None:
        """Select every node. Only effective when `selection_mode='multi'`."""
        self._internal.select_all()

    def clear_selection(self) -> None:
        """Clear the selection."""
        self._internal.clear_selection()

    # ----- events -----

    @overload
    def on_selection_changed(self) -> Stream: ...
    @overload
    def on_selection_changed(self, handler: Callable[[Any], Any]) -> Subscription: ...
    def on_selection_changed(self, handler=None):
        """Fired when the set of selected nodes changes. The handler receives a
        `TreeSelectionEvent` with `nodes` (the full selection, in tree order).

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("selection_changed", handler)

    @overload
    def on_activate(self) -> Stream: ...
    @overload
    def on_activate(self, handler: Callable[[TreeNode], Any]) -> Subscription: ...
    def on_activate(self, handler=None):
        """Fired when a node is activated (double-click or Enter). The handler
        receives the `TreeNode`.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("activate", handler)

    @overload
    def on_expand(self) -> Stream: ...
    @overload
    def on_expand(self, handler: Callable[[TreeNode], Any]) -> Subscription: ...
    def on_expand(self, handler=None):
        """Fired when a node is expanded. The handler receives the `TreeNode`.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("expand", handler)

    @overload
    def on_collapse(self) -> Stream: ...
    @overload
    def on_collapse(self, handler: Callable[[TreeNode], Any]) -> Subscription: ...
    def on_collapse(self, handler=None):
        """Fired when a node is collapsed. The handler receives the `TreeNode`.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("collapse", handler)

    @overload
    def on_right_click(self) -> Stream: ...
    @overload
    def on_right_click(self, handler: Callable[[dict[str, Any]], Any]) -> Subscription: ...
    def on_right_click(self, handler=None):
        """Fired on a right-click. The handler receives a dict with ``node``,
        ``x_root``, and ``y_root`` — enough to position a context menu.

        Returns:
            ``Subscription`` (with handler) or ``Stream`` (without handler).
        """
        return self.on("right_click", handler)


_TREE_EVENTS: dict[str, str] = {
    "selection_changed": "<<TreeSelectionChange>>",
    "activate":          "<<TreeActivate>>",
    "expand":            "<<TreeExpand>>",
    "collapse":          "<<TreeCollapse>>",
    "right_click":       "<<TreeRightClick>>",
}

register_widget_events(Tree, _TREE_EVENTS)
