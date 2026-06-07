"""Internal TreeView — a virtualized recycle view over a tree of TreeNodes.

This is the engine behind the public `Tree`. It mirrors the internal ListView
recycle view (row-widget pool, window recycling, custom scrollbar, keyboard
nav) but its data provider is a *flattened visible-node list* recomputed from
the node hierarchy whenever a branch is expanded, collapsed, or mutated.

Note: this `TreeView` is unrelated to the ttk `TreeView` primitive in
`_impl/primitives/treeview.py` (still used by DataTable). They live in separate
modules and are never imported together.
"""

from __future__ import annotations

from tkinter import TclError
from typing import Any, Callable, Iterator, Literal, Optional

from bootstack.widgets._impl.composites.tree.treeitem import TreeItem, EMPTY
from bootstack.widgets._impl.composites.tree.treenode import TreeNode
from bootstack.widgets._impl.primitives.frame import Frame, FrameKwargs
from bootstack.widgets._impl.primitives.scrollbar import Scrollbar
from bootstack.widgets.types import Master
from typing_extensions import Unpack

VISIBLE_ROWS = 20
ROW_HEIGHT = 32
OVERSCAN_ROWS = 2


class TreeView(Frame):
    """A virtual-scrolling hierarchical view backed by `TreeNode` handles."""

    def __init__(
        self,
        master: Master = None,
        *,
        selection_mode: Literal["none", "single", "multi"] = "single",
        show_selection_controls: bool = False,
        select_on_click: bool = True,
        indent: int = 16,
        striped: bool = False,
        striped_background: str = "background[+1]",
        show_separator: bool = False,
        scrollbar_visibility: Literal["always", "never"] = "always",
        enable_hover: bool = True,
        density: Literal["default", "compact"] = "default",
        **kwargs: Unpack[FrameKwargs],
    ) -> None:
        _user_accent = kwargs.get("accent")
        super().__init__(master, variant="container", ttk_class="ListView.TFrame", **kwargs)
        self._accent = _user_accent or "primary"

        self.winsys = self.tk.call("tk", "windowingsystem")

        self._selection_mode = selection_mode
        self._show_selection_controls = show_selection_controls
        self._select_on_click = select_on_click
        self._indent = indent
        self._striped = striped
        self._striped_background = striped_background
        self._show_separator = show_separator
        self._scrollbar_visibility = scrollbar_visibility
        self._enable_hover = enable_hover
        self._density = density

        # Hierarchy + derived flat view.
        self._roots: list[TreeNode] = []
        self._visible: list[dict] = []

        # Selection / focus state (identity based; survives collapse).
        self._selected: set[TreeNode] = set()
        # Partially-selected parents (tri-state cascade populates this in the
        # multi-select checkpoint); shown as a 'mixed' marker on the control.
        self._mixed: set[TreeNode] = set()
        self._focused_node: Optional[TreeNode] = None

        # Type-ahead.
        self._typeahead = ""
        self._typeahead_after: Optional[str] = None

        # Virtual scrolling state.
        self._start_index = 0
        self._prev_start_index = 0
        self._visible_rows = VISIBLE_ROWS
        self._row_height = ROW_HEIGHT
        self._page_size = VISIBLE_ROWS + OVERSCAN_ROWS
        self._rows: list[TreeItem] = []
        self._mousewheel_bound: set = set()

        from bootstack.style.style import get_style
        self._scrollbar_gutter = get_style().style_builder.scale(6)
        self._scrollbar = Scrollbar(self, orient="vertical", command=self._on_scroll)
        if self._scrollbar_visibility == "always":
            self._scrollbar.pack(side="right", fill="y", padx=(self._scrollbar_gutter, 0))

        self._container = Frame(self, variant="container", ttk_class="ListView.TFrame")
        self._container.pack(side="left", fill="both", expand=True)

        self._ensure_row_pool(self._page_size)

        self.bind("<Configure>", self._on_resize, add="+")
        self._bind_scroll_events(self)
        self._bind_scroll_events(self._container)

        # Row -> container events.
        self._container.bind("<<TreeItemSelect>>", self._on_item_select, add="+")
        self._container.bind("<<TreeItemActivate>>", self._on_item_activate, add="+")
        self._container.bind("<<TreeItemToggle>>", self._on_item_toggle, add="+")
        self._container.bind("<<TreeItemRightClick>>", self._on_item_right_click, add="+")
        self._container.bind("<<TreeItemFocus>>", self._on_item_focus, add="+")

        self._bind_keys(self)
        self._bind_keys(self._container)

        self.after(10, self._remeasure_and_relayout)

    # ================= hierarchy / flatten =================

    def _base_record(self, node: TreeNode, depth: int) -> dict:
        expanded = node.expanded
        if expanded and node.open_icon:
            icon = node.open_icon
        elif not expanded and node.closed_icon:
            icon = node.closed_icon
        else:
            icon = node.icon
        return dict(
            node=node, depth=depth, label=node.label, icon=icon,
            description=node.description, badge=node.badge,
            expandable=node.expandable, expanded=expanded,
        )

    def _flatten(self) -> None:
        out: list[dict] = []

        def walk(nodes: list[TreeNode], depth: int) -> None:
            for n in nodes:
                out.append(self._base_record(n, depth))
                if n.expanded and n.children:
                    walk(n.children, depth + 1)

        walk(self._roots, 0)
        self._visible = out

    def _iter_all_nodes(self) -> Iterator[TreeNode]:
        """Depth-first over every node (including collapsed), in tree order."""
        def walk(nodes: list[TreeNode]) -> Iterator[TreeNode]:
            for n in nodes:
                yield n
                yield from walk(n.children)
        yield from walk(self._roots)

    def _index_of(self, node: TreeNode) -> int:
        for i, rec in enumerate(self._visible):
            if rec["node"] is node:
                return i
        return -1

    @property
    def count(self) -> int:
        return len(self._visible)

    def _on_structure_changed(self) -> None:
        """Re-flatten and relayout after expand/collapse/mutation."""
        self._flatten()
        # Drop selection/focus for nodes no longer in the tree.
        live = set(self._iter_all_nodes())
        self._selected &= live
        self._mixed &= live
        if self._focused_node is not None and self._focused_node not in live:
            self._focused_node = None
        self._remeasure_and_relayout()

    # ================= row pool / recycling =================

    def _ensure_row_pool(self, needed: int) -> None:
        while len(self._rows) < needed:
            row = TreeItem(
                self._container, indent=self._indent, focusable=True,
                hoverable=self._enable_hover, selection_mode=self._selection_mode,
                show_selection_controls=self._show_selection_controls,
                select_on_click=self._select_on_click,
                show_separator=self._show_separator, density=self._density,
                accent=self._accent,
            )
            row.pack(fill="x")
            self._rows.append(row)
            self._bind_keys(row)
            self._apply_widget_surface(row, len(self._rows) - 1)
        while len(self._rows) > needed:
            row = self._rows.pop()
            row.pack_forget()
            try:
                row.destroy()
            except TclError:
                pass

    def _clamp_indices(self) -> None:
        max_start = max(0, self.count - self._visible_rows)
        self._start_index = max(0, min(self._start_index, max_start))

    def _update_rows(self) -> None:
        self._clamp_indices()
        scroll_distance = self._start_index - self._prev_start_index
        if abs(scroll_distance) <= 3 and scroll_distance != 0:
            self._recycle_rows(scroll_distance)
        else:
            self._full_update_rows()
        self._prev_start_index = self._start_index
        total = max(1, self.count)
        first = self._start_index / total
        last = min(1.0, (self._start_index + self._visible_rows) / total)
        self._scrollbar.set(first, last)

    def _recycle_rows(self, scroll_distance: int) -> None:
        if scroll_distance > 0:
            for _ in range(scroll_distance):
                if not self._rows:
                    break
                top = self._rows.pop(0)
                self._update_single_row(top, self._start_index + len(self._rows))
                top.pack_forget()
                top.pack(side="top", fill="x")
                self._rows.append(top)
        elif scroll_distance < 0:
            for _ in range(abs(scroll_distance)):
                if not self._rows:
                    break
                bottom = self._rows.pop()
                self._update_single_row(bottom, self._start_index)
                bottom.pack_forget()
                if self._rows:
                    bottom.pack(side="top", fill="x", before=self._rows[0])
                else:
                    bottom.pack(side="top", fill="x")
                self._rows.insert(0, bottom)

    def _full_update_rows(self) -> None:
        for i, row in enumerate(self._rows):
            self._update_single_row(row, self._start_index + i)

    def _render_record(self, data_index: int) -> dict:
        if data_index < 0 or data_index >= self.count:
            return EMPTY
        base = self._visible[data_index]
        node = base["node"]
        rec = dict(base)
        rec["selected"] = node in self._selected
        rec["focused"] = node is self._focused_node
        rec["mixed"] = node in self._mixed
        rec["item_index"] = data_index
        return rec

    def _update_single_row(self, row: TreeItem, data_index: int) -> None:
        row.update_data(self._render_record(data_index))
        self._bind_mousewheel_recursive(row)

    def _apply_widget_surface(self, row: TreeItem, widget_index: int) -> None:
        base_surface = getattr(self, "_surface", "background")
        if not self._striped:
            surface = base_surface
        else:
            surface = self._striped_background if widget_index % 2 == 1 else base_surface
        if hasattr(row, "set_surface"):
            row.set_surface(surface)

    # ================= scrolling =================

    def _on_scroll(self, *args) -> None:
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self.count - self._visible_rows)
            self._start_index = int(round(fraction * max_start))
        elif args[0] == "scroll":
            amount = int(args[1])
            step = max(1, self._visible_rows // 2) if args[2] == "pages" else 1
            self._start_index += amount * step
        self._clamp_indices()
        self._update_rows()

    def _bind_scroll_events(self, widget) -> None:
        if self.winsys.lower() == "x11":
            widget.bind("<Button-4>", self._on_mousewheel, add="+")
            widget.bind("<Button-5>", self._on_mousewheel, add="+")
        else:
            widget.bind("<MouseWheel>", self._on_mousewheel, add="+")

    def _bind_mousewheel_recursive(self, widget) -> None:
        wid = str(widget)
        if wid not in self._mousewheel_bound:
            self._bind_scroll_events(widget)
            self._mousewheel_bound.add(wid)
        try:
            for child in widget.winfo_children():
                self._bind_mousewheel_recursive(child)
        except Exception:
            pass

    def _on_mousewheel(self, event) -> None:
        under = self.winfo_containing(event.x_root, event.y_root)
        if under is None:
            return
        cur, is_child = under, False
        while cur is not None:
            if cur == self:
                is_child = True
                break
            try:
                cur = cur.master
            except AttributeError:
                break
        if not is_child:
            return
        if self.winsys.lower() == "x11":
            delta = -1 if getattr(event, "num", 0) == 4 else 1
        else:
            delta = -1 if event.delta > 0 else 1
        self._start_index += delta
        self._clamp_indices()
        self._update_rows()

    def _on_resize(self, event) -> None:
        if event.widget == self:
            self.after_idle(self._remeasure_and_relayout)

    def _remeasure_and_relayout(self) -> None:
        if not self._rows:
            return
        rh = self._rows[0].winfo_height()
        if rh <= 1:
            rh = self._rows[0].winfo_reqheight()
        if rh and rh != self._row_height:
            self._row_height = rh
        container_height = self._container.winfo_height()
        if container_height > 0:
            visible = max(1, container_height // max(1, self._row_height))
            page_size = visible + OVERSCAN_ROWS
            if visible != self._visible_rows or page_size != self._page_size:
                self._visible_rows = visible
                self._page_size = page_size
                self._ensure_row_pool(self._page_size)
        self._clamp_indices()
        self._prev_start_index = -999  # force a full update
        self._update_rows()

    # ================= row event handlers =================

    def _on_item_select(self, event) -> None:
        node = event.data
        if not isinstance(node, TreeNode):
            return
        if self._selection_mode == "none":
            self._focused_node = node
            self._update_rows()
        else:
            # single replaces, multi toggles (so a row click with visible
            # checkboxes reads as a checklist) — handled in select().
            self.select(node)

    def _on_item_activate(self, event) -> None:
        node = event.data
        if isinstance(node, TreeNode):
            self._focused_node = node
            # Double-clicking an expandable row toggles it (Explorer convention),
            # in addition to firing the activate event.
            if node.expandable:
                self.toggle(node)
            self._emit("<<TreeActivate>>", node)

    def _on_item_toggle(self, event) -> None:
        node = event.data
        if isinstance(node, TreeNode):
            self.toggle(node)

    def _on_item_right_click(self, event) -> None:
        data = event.data
        if isinstance(data, dict) and isinstance(data.get("node"), TreeNode):
            self._focused_node = data["node"]
            self._update_rows()
            self._emit("<<TreeRightClick>>", data)

    def _on_item_focus(self, event) -> None:
        node = event.data
        if isinstance(node, TreeNode):
            self._focused_node = node

    def _emit(self, sequence: str, data: Any) -> None:
        try:
            self.event_generate(sequence, data=data)
        except TclError:
            pass

    # ================= public-ish API (called by the wrapper) =================

    def add(self, label: str = "", *, parent: Optional[TreeNode] = None,
            children: Optional[list] = None, index: Optional[int] = None,
            **kwargs: Any) -> TreeNode:
        node = TreeNode(label, **kwargs)
        node._tree = self
        node.parent = parent
        siblings = parent.children if parent is not None else self._roots
        if index is None:
            siblings.append(node)
        else:
            siblings.insert(index, node)
        if children:
            for spec in children:
                self._add_from_spec(spec, parent=node)
        self._on_structure_changed()
        return node

    def _add_from_spec(self, spec: Any, parent: TreeNode) -> TreeNode:
        """Add a node from a dict spec (declarative `nodes=`) or a TreeNode."""
        if isinstance(spec, TreeNode):
            spec._tree = self
            spec.parent = parent
            parent.children.append(spec)
            for child in list(spec.children):
                child._tree = self
            return spec
        if isinstance(spec, str):
            spec = {"label": spec}
        spec = dict(spec)
        children = spec.pop("children", None)
        node = TreeNode(**spec)
        node._tree = self
        node.parent = parent
        parent.children.append(node)
        if children:
            for child_spec in children:
                self._add_from_spec(child_spec, parent=node)
        return node

    def load(self, specs: list) -> None:
        """Replace the whole tree from a declarative list of specs."""
        self._roots = []
        self._selected.clear()
        self._focused_node = None
        for spec in specs or []:
            self._add_root_from_spec(spec)
        self._on_structure_changed()

    def _add_root_from_spec(self, spec: Any) -> TreeNode:
        if isinstance(spec, TreeNode):
            spec._tree = self
            spec.parent = None
            self._roots.append(spec)
            return spec
        if isinstance(spec, str):
            spec = {"label": spec}
        spec = dict(spec)
        children = spec.pop("children", None)
        node = TreeNode(**spec)
        node._tree = self
        node.parent = None
        self._roots.append(node)
        if children:
            for child_spec in children:
                self._add_from_spec(child_spec, parent=node)
        return node

    def remove(self, node: TreeNode) -> None:
        siblings = node.parent.children if node.parent is not None else self._roots
        try:
            siblings.remove(node)
        except ValueError:
            return
        self._on_structure_changed()

    def move(self, node: TreeNode, new_parent: Optional[TreeNode], index: Any = "end") -> None:
        siblings = node.parent.children if node.parent is not None else self._roots
        try:
            siblings.remove(node)
        except ValueError:
            return
        node.parent = new_parent
        target = new_parent.children if new_parent is not None else self._roots
        if index == "end" or index is None or index >= len(target):
            target.append(node)
        else:
            target.insert(int(index), node)
        self._on_structure_changed()

    def clear(self) -> None:
        self._roots = []
        self._selected.clear()
        self._focused_node = None
        self._on_structure_changed()

    # ---- expansion ----

    def expand(self, node: TreeNode) -> None:
        if not node.expandable:
            return
        if node.loader is not None and not node._loaded:
            self._load_children(node)
        if not node.expanded:
            node.expanded = True
            self._on_structure_changed()
            self._emit("<<TreeExpand>>", node)

    def collapse(self, node: TreeNode) -> None:
        if node.expanded:
            node.expanded = False
            self._on_structure_changed()
            self._emit("<<TreeCollapse>>", node)

    def toggle(self, node: TreeNode) -> None:
        if node.expanded:
            self.collapse(node)
        else:
            self.expand(node)

    def _load_children(self, node: TreeNode) -> None:
        # Mark loaded up front so a re-entrant expand during the loader call
        # can't trigger a second load. Loaders should handle their own errors;
        # a raising loader yields an empty (leaf) node.
        node._loaded = True
        try:
            result = node.loader(node) if node.loader else None
        except Exception:
            result = None
        for spec in (result or []):
            self._add_from_spec(spec, parent=node)
        # Deferred cascade: if this parent was selected while its lazy children
        # were still unloaded, the freshly loaded children inherit that state.
        if node in self._selected:
            for child in node.children:
                self._set_subtree_selected(child, True)

    def reload_children(self, node: TreeNode) -> None:
        """Refresh a lazy node: drop its loaded children and fetch them again.

        Only meaningful for nodes created with a `loader`. If the node is
        expanded the children reload immediately; otherwise they reload on the
        next expand. A no-op for non-lazy nodes.
        """
        if node.loader is None:
            return
        node.children = []
        node._loaded = False
        if node.expanded:
            self._load_children(node)
        self._on_structure_changed()

    def expand_all(self) -> None:
        for node in list(self._iter_all_nodes()):
            if node.loader is not None and not node._loaded:
                self._load_children(node)
            if node.expandable:
                node.expanded = True
        self._on_structure_changed()

    def collapse_all(self) -> None:
        for node in self._iter_all_nodes():
            node.expanded = False
        self._on_structure_changed()

    def reveal(self, node: TreeNode) -> None:
        for anc in list(node.ancestors()):
            if anc.loader is not None and not anc._loaded:
                self._load_children(anc)
            anc.expanded = True
        self._flatten()
        self._focused_node = node
        idx = self._index_of(node)
        if idx >= 0:
            self._scroll_into_view(idx)
        self._update_rows()

    # ---- selection ----

    def _emit_selection_changed(self) -> None:
        from bootstack.events import TreeSelectionEvent
        self._emit("<<TreeSelectionChange>>", TreeSelectionEvent(nodes=self.get_selected()))

    def _set_subtree_selected(self, node: TreeNode, selected: bool) -> None:
        """Select/deselect a node and cascade to its LOADED descendants.

        A node with unloaded lazy children is set on its own (deferred cascade);
        its children inherit the state when they load (see `_load_children`).
        """
        if node.loader is not None and not node._loaded:
            targets = [node]            # defer cascade until children load
        else:
            targets = [node, *node.descendants()]
        for n in targets:
            if selected:
                self._selected.add(n)
                self._mixed.discard(n)
            else:
                self._selected.discard(n)
                self._mixed.discard(n)

    def _recompute_ancestors(self, node: TreeNode) -> None:
        """Recompute each ancestor's tri-state from its children."""
        for anc in node.ancestors():
            kids = anc.children
            if not kids:
                continue
            n_selected = sum(1 for c in kids if c in self._selected)
            any_mixed = any(c in self._mixed for c in kids)
            if not any_mixed and n_selected == len(kids):
                self._selected.add(anc)
                self._mixed.discard(anc)
            elif not any_mixed and n_selected == 0:
                self._selected.discard(anc)
                self._mixed.discard(anc)
            else:
                self._selected.discard(anc)
                self._mixed.add(anc)

    def select(self, node: TreeNode) -> None:
        if self._selection_mode == "none":
            return
        if self._selection_mode == "single":
            self._selected = {node}
            self._mixed.clear()
        else:
            # Tri-state cascade: toggle the node's whole subtree, then refresh
            # ancestors. A mixed (partial) parent toggles ON (selects all).
            self._set_subtree_selected(node, node not in self._selected)
            self._recompute_ancestors(node)
        self._focused_node = node
        self._update_rows()
        self._emit_selection_changed()

    def deselect(self, node: TreeNode) -> None:
        if node in self._selected or node in self._mixed:
            self._set_subtree_selected(node, False)
            self._recompute_ancestors(node)
            self._update_rows()
            self._emit_selection_changed()

    def select_all(self) -> None:
        if self._selection_mode != "multi":
            return
        self._selected = set(self._iter_all_nodes())
        self._mixed.clear()
        self._update_rows()
        self._emit_selection_changed()

    def clear_selection(self) -> None:
        if self._selected or self._mixed:
            self._selected.clear()
            self._mixed.clear()
            self._update_rows()
            self._emit_selection_changed()

    def get_selected(self) -> list[TreeNode]:
        sel = self._selected
        return [n for n in self._iter_all_nodes() if n in sel]

    # ================= keyboard navigation =================

    def _bind_keys(self, widget) -> None:
        widget.bind("<Down>", self._on_down, add="+")
        widget.bind("<Up>", self._on_up, add="+")
        widget.bind("<Left>", self._on_left, add="+")
        widget.bind("<Right>", self._on_right, add="+")
        widget.bind("<Home>", self._on_home, add="+")
        widget.bind("<End>", self._on_end, add="+")
        widget.bind("<Return>", self._on_return, add="+")
        widget.bind("<space>", self._on_space, add="+")
        widget.bind("<Key>", self._on_typeahead, add="+")

    def _scroll_into_view(self, index: int) -> None:
        if index < self._start_index:
            self._start_index = index
            self._clamp_indices()
        elif index >= self._start_index + self._visible_rows:
            self._start_index = index - self._visible_rows + 1
            self._clamp_indices()

    def _focus_index(self, index: int) -> str:
        if self.count == 0 or index < 0 or index >= self.count:
            return "break"
        self._scroll_into_view(index)
        self._focused_node = self._visible[index]["node"]
        self._update_rows()
        visual = index - self._start_index
        if 0 <= visual < len(self._rows):
            try:
                # Keyboard navigation -> show the focus ring (visual_focus).
                self._rows[visual].focus_set(visual_focus=True)
            except TclError:
                pass
        return "break"

    def _focused_index(self) -> int:
        if self._focused_node is None:
            return -1
        return self._index_of(self._focused_node)

    def _on_down(self, event) -> str:
        if self.count == 0:
            return "break"
        cur = self._focused_index()
        nxt = self._start_index if cur < 0 else min(cur + 1, self.count - 1)
        return self._focus_index(nxt)

    def _on_up(self, event) -> str:
        if self.count == 0:
            return "break"
        cur = self._focused_index()
        nxt = self._start_index if cur < 0 else max(cur - 1, 0)
        return self._focus_index(nxt)

    def _on_left(self, event) -> str:
        node = self._focused_node
        if node is None:
            return "break"
        if node.expandable and node.expanded:
            self.collapse(node)
            return self._focus_index(self._index_of(node))
        if node.parent is not None:
            return self._focus_index(self._index_of(node.parent))
        return "break"

    def _on_right(self, event) -> str:
        node = self._focused_node
        if node is None:
            return "break"
        if node.expandable and not node.expanded:
            self.expand(node)
            return self._focus_index(self._index_of(node))
        if node.children:
            return self._focus_index(self._index_of(node.children[0]))
        return "break"

    def _on_home(self, event) -> str:
        return self._focus_index(0)

    def _on_end(self, event) -> str:
        return self._focus_index(self.count - 1)

    def _on_return(self, event) -> str:
        node = self._focused_node
        if node is not None:
            self._emit("<<TreeActivate>>", node)
        return "break"

    def _on_space(self, event) -> str:
        node = self._focused_node
        if node is None:
            return "break"
        # Space toggles selection (in multi, this is the checklist toggle).
        self.select(node)
        return "break"

    def _on_typeahead(self, event) -> Optional[str]:
        ch = event.char
        if not ch or not ch.isprintable() or ch in (" ",):
            return None
        self._typeahead += ch.lower()
        if self._typeahead_after is not None:
            try:
                self.after_cancel(self._typeahead_after)
            except Exception:
                pass
        self._typeahead_after = self.after(700, self._clear_typeahead)
        start = max(0, self._focused_index())
        order = list(range(start + 1, self.count)) + list(range(0, start + 1))
        for i in order:
            label = (self._visible[i]["label"] or "").lower()
            if label.startswith(self._typeahead):
                return self._focus_index(i)
        return "break"

    def _clear_typeahead(self) -> None:
        self._typeahead = ""
        self._typeahead_after = None

    @property
    def roots(self) -> list[TreeNode]:
        return self._roots
