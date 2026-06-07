"""TreeItem — a single recycled row in the Tree's virtual view.

Mirrors `ListItem` (a `CompositeFrame` composing on-demand child widgets with
synchronized hover/focus/selected state) and adds the two things a tree row
needs that a flat list row does not: a depth indent and an expander chevron.

A row is recycled: `update_data(record)` re-points it at whichever visible node
currently occupies its slot. The record is built by the internal `TreeView`.
"""

from __future__ import annotations

from tkinter import TclError
from typing import Any, Optional

from bootstack.widgets._impl.composites.compositeframe import CompositeFrame
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets.types import Master


# Empty-slot sentinel (a record with this key hides the row).
EMPTY = {"__empty__": True}


class TreeItem(CompositeFrame):
    """A recycled tree row: indent, chevron, icon, label, description, badge."""

    def __init__(
        self,
        master: Master = None,
        *,
        indent: int = 16,
        chevron_width: int = 26,
        focusable: bool = True,
        hoverable: bool = True,
        selection_mode: str = "single",
        show_selection_controls: bool = False,
        select_on_click: bool = True,
        show_separator: bool = False,
        density: str = "default",
        accent: Optional[str] = None,
    ) -> None:
        self._data: dict = {}
        self._state: dict = {}
        self._node = None
        self._item_index = 0

        self._indent = indent
        self._chevron_width = chevron_width
        self._focusable = focusable
        self._hoverable = hoverable
        self._selection_mode = selection_mode
        self._show_selection_controls = show_selection_controls
        self._select_on_click = select_on_click
        self._show_separator = show_separator
        self._density = density
        self._accent = accent or "primary"
        # When the selection control is visible it IS the selection indicator,
        # so the row wash is suppressed (VS Code / installer style).
        self._wash = not show_selection_controls

        item_padding = (6, 3) if density == "compact" else (8, 4)

        super().__init__(
            master=master,
            select_on_click=False,
            variant="separated_item" if show_separator else "item",
            takefocus=focusable,
            ttk_class="ListView.TFrame",
            padding=item_padding,
            accent=self._accent,
            style_options=dict(hoverable=hoverable, density=density, wash=self._wash),
        )

        style_opts = dict(hoverable=hoverable, density=density, wash=self._wash)

        # Left region: [<indent padx> chevron-slot][checkbox?][icon]
        self._left_frame = Frame(
            self, variant="list", ttk_class="ListView.TFrame",
            takefocus=False, accent=self._accent, style_options=style_opts,
        )
        self._left_frame.pack(side="left", fill="y")

        self._center_frame = Frame(
            self, variant="list", ttk_class="ListView.TFrame",
            takefocus=False, accent=self._accent, style_options=style_opts,
        )
        self._center_frame.pack(side="left", fill="x", expand=True)

        self._right_frame = Frame(
            self, variant="list", ttk_class="ListView.TFrame",
            takefocus=False, accent=self._accent, style_options=style_opts,
        )
        self._right_frame.pack(side="left")

        # Fixed-width chevron slot. The chevron button is PLACED inside it (place
        # children don't influence the slot's requested width), so the gutter is
        # exactly `chevron_width` whether or not a chevron is shown — leaf and
        # parent rows at the same depth line up perfectly. The depth indent is
        # applied as LEFT PADDING on this slot via pack_configure: a ttk frame
        # won't shrink its -width back down once set, so a width-resized spacer
        # goes stale on recycle; padx is reliable and the gap shows the left
        # frame's background (which already follows the row's wash).
        self._chevron_slot = Frame(
            self._left_frame, variant="list", ttk_class="ListView.TFrame",
            takefocus=False, accent=self._accent, style_options=style_opts,
            width=chevron_width,
        )
        self._chevron_slot.pack(side="left", fill="y")
        self._chevron_btn: Optional[Button] = None

        self.register_composite(self._chevron_slot)

        self._select_ctrl: Optional[Label] = None
        self._icon_widget: Optional[Label] = None
        self._label_widget: Optional[Label] = None
        self._desc_widget: Optional[Label] = None
        self._badge_widget: Optional[Label] = None

        self._separator = Separator(self)

        for w in (self._left_frame, self._center_frame, self._right_frame):
            self.register_composite(w)

        # Selection control (checkbox for multi, radio for single) — the visible
        # affordance for selection, the same 'selection' variant ListView uses.
        # Its fill is driven by the row's 'selected' state via the coordinator;
        # the 'alternate' state shows a partially-selected (mixed) parent.
        if self._show_selection_controls and self._selection_mode != "none":
            if self._selection_mode == "multi":
                glyph = dict(name="square", state=[
                    ("selected", "check-square-fill"),
                    ("alternate", "dash-square-fill"),
                ])
            else:
                glyph = dict(name="circle", state=[("selected", "check-circle-fill")])
            self._select_ctrl = Label(
                self._left_frame, icon=glyph, variant="selection",
                ttk_class="ListView.TLabel", icon_only=True, accent=self._accent,
                takefocus=False, style_options=self._style_opts(),
            )
            self._select_ctrl.pack(side="left", after=self._chevron_slot, padx=(0, 4))
            self.register_composite(self._select_ctrl)
            # When the row itself doesn't select on click, the control still must
            # — give it its own click path (the row's invoke is gated below).
            if not self._select_on_click:
                self._select_ctrl.bind("<Button-1>", self._on_ctrl_click, add="+")

        # Row interactions. Double-/right-click must be bound on the leaf widgets
        # too — a click lands on the label/icon, not the row frame, and Tk does
        # not propagate it to the parent's bindings.
        if self._focusable:
            self.on_invoked(self._on_invoke)
            self.bind("<FocusIn>", self._on_focus_in, add="+")
        for w in (self, self._left_frame, self._center_frame, self._right_frame,
                  self._chevron_slot):
            self._bind_row_mouse(w)

    # ----- helpers -----

    def _style_opts(self) -> dict:
        return dict(hoverable=self._hoverable, density=self._density, wash=self._wash)

    def _bind_row_mouse(self, widget) -> None:
        """Bind double-click (activate) and right-click on a row-level widget."""
        widget.bind("<Double-Button-1>", self._on_activate, add="+")
        widget.bind("<Button-3>", self._on_right_click, add="+")
        widget.bind("<Button-2>", self._on_right_click, add="+")  # mac

    @property
    def node(self):
        """The TreeNode currently rendered in this row (or None)."""
        return self._node

    # ----- row -> container events -----

    def _emit(self, sequence: str, data: Any) -> None:
        try:
            self.master.event_generate(sequence, data=data)
        except TclError:
            pass

    def _on_invoke(self, event) -> None:
        if self._node is None:
            return
        if self._focusable:
            self.focus()
        # When select_on_click is off, a row click only focuses (the selection
        # control is the sole way to select). The control routes through
        # _on_ctrl_click in that case.
        if self._select_on_click:
            self._emit("<<TreeItemSelect>>", self._node)

    def _on_ctrl_click(self, event=None) -> str:
        if self._node is not None:
            if self._focusable:
                self.focus()
            self._emit("<<TreeItemSelect>>", self._node)
        return "break"

    def _on_focus_in(self, event) -> None:
        if self._node is not None:
            self._emit("<<TreeItemFocus>>", self._node)

    def _on_activate(self, event=None) -> str:
        if self._node is not None:
            self._emit("<<TreeItemActivate>>", self._node)
        return "break"

    def _on_right_click(self, event) -> str:
        if self._node is not None:
            self._emit(
                "<<TreeItemRightClick>>",
                {"node": self._node, "x_root": event.x_root, "y_root": event.y_root},
            )
        return "break"

    def _on_chevron(self) -> None:
        if self._node is not None:
            self._emit("<<TreeItemToggle>>", self._node)

    # ----- widget updates -----

    def _update_chevron(self, expandable: bool, expanded: bool) -> None:
        if expandable:
            icon = "chevron-down" if expanded else "chevron-right"
            if self._chevron_btn is None:
                self._chevron_btn = Button(
                    self._chevron_slot, icon=icon, icon_only=True, variant="icon",
                    ttk_class="ListView.TButton", takefocus=False,
                    accent=self._accent, command=self._on_chevron,
                    style_options=self._style_opts(),
                )
                self.register_composite(self._chevron_btn)
            else:
                self._chevron_btn.configure(icon=icon)
            if not self._chevron_btn.winfo_manager():
                self._chevron_btn.place(relx=0.5, rely=0.5, anchor="center")
        else:
            if self._chevron_btn is not None:
                self._chevron_btn.place_forget()

    def set_mixed(self, mixed: bool) -> None:
        """Mark the selection control as a partially-selected (mixed) parent.

        Driven explicitly (not by the coordinator) so it survives selection
        state updates. Used by tri-state cascade.
        """
        if self._select_ctrl is not None:
            self._select_ctrl.state(("alternate",) if mixed else ("!alternate",))

    def _update_icon(self, icon: Optional[str]) -> None:
        if icon:
            if self._icon_widget is None:
                self._icon_widget = Label(
                    self._left_frame, icon=icon, variant="icon",
                    ttk_class="ListView.TLabel", takefocus=False, icon_only=True,
                    accent=self._accent, style_options=self._style_opts(),
                )
                self._icon_widget.pack(side="left", padx=(0, 5))
                self.register_composite(self._icon_widget)
                self._bind_row_mouse(self._icon_widget)
            else:
                self._icon_widget.configure(icon=icon)
        elif self._icon_widget is not None:
            self._destroy_widget("_icon_widget")

    def _update_label(self, text: Optional[str]) -> None:
        font = "caption" if self._density == "compact" else "body"
        if text is not None:
            if self._label_widget is None:
                self._label_widget = Label(
                    self._center_frame, text=text, font=font, variant="list",
                    ttk_class="ListView.TLabel", takefocus=False,
                    accent=self._accent, style_options=self._style_opts(),
                )
                self._label_widget.pack(side="left", anchor="w")
                self.register_composite(self._label_widget)
                self._bind_row_mouse(self._label_widget)
            else:
                self._label_widget.configure(text=text)
        elif self._label_widget is not None:
            self._destroy_widget("_label_widget")

    def _update_description(self, text: Optional[str]) -> None:
        if text:
            if self._desc_widget is None:
                self._desc_widget = Label(
                    self._center_frame, text=text, font="caption", variant="list",
                    ttk_class="ListView.TLabel", takefocus=False,
                    accent=self._accent, style_options=self._style_opts(),
                )
                self._desc_widget.pack(side="left", anchor="w", padx=(6, 0))
                self.register_composite(self._desc_widget)
                self._bind_row_mouse(self._desc_widget)
            else:
                self._desc_widget.configure(text=text)
        elif self._desc_widget is not None:
            self._destroy_widget("_desc_widget")

    def _update_badge(self, text: Optional[str]) -> None:
        if text:
            if self._badge_widget is None:
                # Trailing metadata as a small caption that follows the row wash
                # (registered composite). A dedicated crisp tree-badge style
                # (pill with proper hover) is a future enhancement.
                self._badge_widget = Label(
                    self._right_frame, text=text, font="caption", variant="list",
                    ttk_class="ListView.TLabel", accent=self._accent,
                    takefocus=False, style_options=self._style_opts(),
                )
                self._badge_widget.pack(side="right", padx=6)
                self.register_composite(self._badge_widget)
                self._bind_row_mouse(self._badge_widget)
            else:
                self._badge_widget.configure(text=text)
        elif self._badge_widget is not None:
            self._destroy_widget("_badge_widget")

    def _destroy_widget(self, attr: str) -> None:
        w = getattr(self, attr, None)
        if w is not None:
            # Unregister BEFORE destroy so a later hover/state update doesn't
            # call .state() on a dead widget.
            try:
                self.unregister_composite(w)
            except Exception:
                pass
            try:
                w.pack_forget()
                w.destroy()
            except TclError:
                pass
            setattr(self, attr, None)

    # ----- surface (striping) -----

    def set_surface(self, surface: str) -> None:
        """Set the row + container surface color (used for striped rows)."""
        previous = getattr(self, "_surface", "background")
        self.configure_style_options(surface=surface)
        if previous != surface:
            self.rebuild_style()
        targets = [self._left_frame, self._center_frame, self._right_frame,
                   self._chevron_slot]
        if self._select_ctrl is not None:
            targets.append(self._select_ctrl)
        for frame in targets:
            try:
                frame.configure_style_options(surface=surface)
                frame.rebuild_style()
            except Exception:
                continue

    # ----- recycle entry point -----

    def update_data(self, record: Optional[dict]) -> None:
        """Re-point this row at the node in `record`, or hide it if empty."""
        if record is None or "__empty__" in record:
            self._node = None
            self.pack_forget()
            return

        if not self.winfo_manager():
            self.pack(fill="x")

        self._data = record
        self._node = record.get("node")
        self._item_index = record.get("item_index", 0)

        # Indent reflects depth, applied as left padding on the chevron slot.
        depth = record.get("depth", 0)
        if self._state.get("depth") != depth:
            self._chevron_slot.pack_configure(padx=(max(0, depth * self._indent), 0))
            self._state["depth"] = depth

        # Focus. (The keyboard-focus ring rides the 'background' state, set by
        # the keyboard nav via focus_set(visual_focus=True). When a row stops
        # being the focused node, drop that state so a recycled/relocated row
        # doesn't keep a stale ring.)
        focused = bool(record.get("focused", False))
        if self._state.get("focused") != focused:
            if focused and self._focusable:
                try:
                    self.focus_set()
                except TclError:
                    pass
            elif not focused:
                try:
                    self.state(["!background"])
                except TclError:
                    pass
            self._state["focused"] = focused

        # Chevron (re-pack only when the expandable/expanded pair changes).
        chev = (bool(record.get("expandable", False)), bool(record.get("expanded", False)))
        if self._state.get("chevron") != chev:
            self._update_chevron(*chev)
            self._state["chevron"] = chev

        # Content widgets (diffed against last render).
        for field, updater in (
            ("icon", self._update_icon),
            ("label", self._update_label),
            ("description", self._update_description),
            ("badge", self._update_badge),
        ):
            value = record.get(field)
            if self._state.get(field) != value:
                updater(value)
                self._state[field] = value

        # Selection highlight — drives the row wash AND the selection control's
        # fill (the control follows the coordinator's 'selected' state).
        selected = bool(record.get("selected", False))
        if self._state.get("selected") != selected:
            self.set_selected(selected)
            self._state["selected"] = selected

        # Mixed (partially-selected parent) marker on the selection control.
        mixed = bool(record.get("mixed", False))
        if self._state.get("mixed") != mixed:
            self.set_mixed(mixed)
            self._state["mixed"] = mixed
