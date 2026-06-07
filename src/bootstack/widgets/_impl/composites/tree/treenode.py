"""TreeNode — the object handle for nodes in the Tree widget.

A `TreeNode` is a plain Python object (not a Tk widget) that the user holds and
passes back to the tree. It carries display configuration, an opaque data bag,
and its place in the hierarchy. Structural changes route back to the owning tree
so the view re-renders.
"""

from __future__ import annotations

from typing import Any, Callable, Iterator, Optional

# Sentinel separating recognized display parameters from the user data bag.
_DISPLAY_PARAMS = frozenset(
    {"label", "icon", "open_icon", "closed_icon", "description", "badge",
     "expanded", "children", "loader"}
)


class TreeNode:
    """A single node in a `Tree`.

    Nodes are identity-based handles: hold the object returned by `Tree.add()`
    and pass it back to `expand()`, `select()`, `remove()`, and friends. Two
    nodes are never equal unless they are the same object.

    Display attributes (`label`, `icon`, `description`, `badge`, ...) are a
    non-destructive view over the node. Any keyword not recognized as a display
    parameter is folded into `data`, so a handler always gets the user's domain
    data back.
    """

    __slots__ = (
        "label", "icon", "open_icon", "closed_icon", "description", "badge",
        "expanded", "children", "parent", "data", "loader",
        "_tree", "_loaded",
    )

    def __init__(
        self,
        label: str = "",
        *,
        icon: Optional[str] = None,
        open_icon: Optional[str] = None,
        closed_icon: Optional[str] = None,
        description: Optional[str] = None,
        badge: Optional[str] = None,
        expanded: bool = False,
        loader: Optional[Callable[["TreeNode"], Any]] = None,
        data: Optional[dict] = None,
        **extra: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.open_icon = open_icon
        self.closed_icon = closed_icon
        self.description = description
        self.badge = badge
        self.expanded = expanded
        self.loader = loader

        self.children: list[TreeNode] = []
        self.parent: Optional[TreeNode] = None

        # The data bag: explicit data= merged with any overflow kwargs. Nothing
        # consumed by a display parameter ever lands here; nothing else is lost.
        self.data: dict = dict(data or {})
        self.data.update(extra)

        # Owning internal TreeView (set when attached); used to request renders.
        self._tree = None
        # Lazy-loading state: a node with a loader is "expandable" before its
        # children exist; _loaded flips True after the loader runs once.
        self._loaded = loader is None

    # ----- structure -----

    @property
    def is_leaf(self) -> bool:
        """Whether this node has no children and cannot lazily load any."""
        return not self.children and self.loader is None

    @property
    def expandable(self) -> bool:
        """Whether this node can be expanded (has children or a lazy loader)."""
        return bool(self.children) or (self.loader is not None and not self._loaded)

    @property
    def depth(self) -> int:
        """Distance from the root (root nodes are depth 0)."""
        d = 0
        p = self.parent
        while p is not None:
            d += 1
            p = p.parent
        return d

    def ancestors(self) -> Iterator["TreeNode"]:
        """Yield this node's parent, grandparent, ... up to the root."""
        p = self.parent
        while p is not None:
            yield p
            p = p.parent

    def descendants(self) -> Iterator["TreeNode"]:
        """Yield every node beneath this one, depth-first."""
        for child in self.children:
            yield child
            yield from child.descendants()

    # ----- convenience mutation (routes to the owning tree) -----

    def add(self, label: str = "", **kwargs: Any) -> "TreeNode":
        """Add a child node under this node and return it.

        Args:
            label: The child's display label.
            **kwargs: Forwarded to `Tree.add` (icon, description, badge,
                expanded, children, loader, data, and overflow data kwargs).
        """
        if self._tree is None:
            raise RuntimeError("node is not attached to a tree")
        return self._tree.add(label, parent=self, **kwargs)

    def remove(self) -> None:
        """Remove this node (and its descendants) from the tree."""
        if self._tree is not None:
            self._tree.remove(self)

    def expand(self) -> None:
        """Expand this node to reveal its children."""
        if self._tree is not None:
            self._tree.expand(self)

    def collapse(self) -> None:
        """Collapse this node to hide its children."""
        if self._tree is not None:
            self._tree.collapse(self)

    def reload_children(self) -> None:
        """Refresh a lazy node's children (drop and re-fetch via its loader)."""
        if self._tree is not None:
            self._tree.reload_children(self)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"TreeNode(label={self.label!r}, children={len(self.children)})"
