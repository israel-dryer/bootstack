from tkinter import Toplevel

from typing_extensions import Unpack

from typing import Any

from bootstack.events import ChangeEvent
from bootstack.widgets._core.options import (
    cluster_records,
    normalize_options,
    option_display,
    option_is_icon_only,
    record_to_dict,
)
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets._impl.composites.scrollview import ScrollView
from bootstack.widgets._impl.composites.field import Field, FieldOptions
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master, Option


class SelectBox(Field):
    """Dropdown-like field widget built on top of Field.

    Renders a field with a suffix button that opens a popup list of available
    items. Selecting an item updates the field value and emits `<<Change>>`.
    """

    _POPUP_MAX_HEIGHT = 200  # px — popup never exceeds this, but shrinks to fit fewer items

    def __init__(
            self,
            master: Master = None,
            value: Any = None,
            items: list[Option] = None,
            label: str = None,
            message: str = None,
            allow_custom_values: bool = False,
            strict_value: bool = False,
            show_dropdown_button: bool = True,
            dropdown_button_icon: str = None,
            enable_search: bool = False,
            group_by: str = None,
            max_visible_items: int = None,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial selected value (value-space). Should match one of the
                options unless `allow_custom_values` is set.
            items: Options to present in the popup — each a string,
                `(text, value)` tuple, or `{'text', 'value'}` dict. The popup
                and field display each option's text; the selected value is
                emitted in value-space. A dict option may also carry `'icon'`
                (rendered beside the row label) and `'disabled'` (when `True` the
                row is dimmed and cannot be chosen).
            label: Optional label text shown above the field.
            message: Optional helper/error message shown below the field.
            allow_custom_values: If True, the entry is editable so users can type
                arbitrary values in addition to choosing from the list.
            show_dropdown_button: If True (default), the dropdown button is shown. This option is
                ignored if custom values are allowed.
            dropdown_button_icon: The icon to display on the dropdown button.
            enable_search: If True, allows typing in the entry to filter the popup list.
                When combined with allow_custom_values=False, the first filtered item is selected
                when the popup closes. With allow_custom_values=True, any typed value is kept.
            group_by: Name of an option field to cluster the popup rows under
                non-selectable group headers (e.g. `'category'`). The field is
                read from each option's flat record, so it may be any carried bag
                key (or `'text'`/`'value'`). Groups appear in first-appearance
                order; options missing the field render headerless. Grouping is
                presentational only — `value`/`selection` are unaffected. None
                (default) renders a flat list.
            max_visible_items: Approximate number of option rows the popup shows
                before it scrolls (height is `max_visible_items * row_height`).
                Group headers and separators consume some of that budget, so the
                count is approximate. None (default) uses the built-in cap.

        Other Parameters:
            allow_blank: If True, empty input is allowed.
            accent: Accent token for styling the focus ring and active border.
            value_format: ICU format pattern for parsing/formatting.
            font: Font for text display.
            foreground: Text color.
            initial_focus: If True, widget receives focus when created.
            justify: Text justification ('left', 'center', 'right').
            show_message: If True, displays message text below the field.
            padding: Padding around the entry widget.
            state: The widget state ('normal', 'disabled', 'readonly').
            textvariable: Tkinter Variable to link with the entry text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal object for reactive text updates.
            width: Width of the entry in characters.
            required: If True, field cannot be empty.
        """
        # Localization mode for option display (entry face + popup rows). None
        # defers to the app's localize_mode; False keeps the raw labels.
        self._localize = kwargs.pop('localize', None)
        # Normalize options once. The maps only decouple an option's *display
        # text* from its *value*; the entry keeps owning the raw value (so
        # `value_format` parsing, e.g. TimeField's time objects, is preserved).
        # When localization is active the display text is the translated label,
        # so a plain option is treated like a decoupled one (display != value).
        self._records = normalize_options(items)
        self._allow_custom_values = allow_custom_values
        self._strict_value = strict_value
        self._rebuild_option_maps()

        # Forward an explicit localize mode to Field so the label/message follow
        # it too; when unset, Field keeps its own 'auto' default.
        if self._localize is not None:
            kwargs['localize'] = self._localize

        # Seed the entry with the display form of the initial value.
        super().__init__(master, value=self._resolve_display(value), label=label, message=message, **kwargs)

        # Re-translate the displayed text + option maps on a live locale switch.
        self.winfo_toplevel().bind('<<LocaleChanged>>', self._on_locale_changed_refresh, add='+')

        self._search_enabled = enable_search
        self._group_by = group_by
        self._max_visible_items = max_visible_items
        self._popup_open = False
        self._popup_state = None
        self._dropdown_button_icon = dropdown_button_icon or 'chevron-down'
        self._popup_frame = None
        self._popup_inner = None
        self._item_labels = []
        self._group_headers = []

        # Add dropdown button if needed
        if allow_custom_values or show_dropdown_button:
            self.insert_addon(
                Button,
                position="after",
                name="dropdown",
                icon=self._dropdown_button_icon,
                icon_only=True,
                command=self._on_dropdown_click
            )

        # Configure entry state based on search and custom value settings
        if allow_custom_values or enable_search:
            self.entry_widget.state(['!readonly'])
        else:
            # Set entry to readonly but keep dropdown button enabled
            self.entry_widget.state(['readonly'])
            self.after_idle(self._bind_readonly_selection_on_click)

    # ----- Option normalization + value<->text mapping -----

    def _effective_localize(self, item_mode: Any = None) -> Any:
        """Resolve the active localize mode, deferring to the app when unset.

        A per-option `item_mode` (its `localize` bag key) wins; then the
        widget-level mode; then the app's `localize_mode`.
        """
        if item_mode is not None:
            return item_mode
        if self._localize is not None:
            return self._localize
        try:
            from bootstack._runtime.app import get_app_settings
            return get_app_settings().localize_mode
        except Exception:
            return 'auto'

    def _display_text(self, raw: str, item_mode: Any = None) -> str:
        """Map a raw option label to its display text under the active mode.

        Returns the label unchanged when localization is off or no translation
        is registered; otherwise the catalog translation.
        """
        if not raw:
            return raw
        if self._effective_localize(item_mode) is False:
            return raw
        try:
            from bootstack.i18n import MessageCatalog
            return MessageCatalog.translate(raw) or raw
        except Exception:
            return raw

    def _record_display(self, rec) -> str:
        """The display text for one option record (honoring its localize key)."""
        return self._display_text(rec.text, rec.extras.get('localize'))

    def _rebuild_option_maps(self) -> None:
        """Rebuild displaytext<->value lookups from the current records.

        Maps are keyed on each option's *display* text (the translated label
        when localization is active), so the entry's shown text round-trips to
        the option value. Duplicate display texts keep the first value;
        duplicate values keep the first text. Popup selection resolves by the
        chosen row's record, so duplicate texts with distinct values still
        select correctly from the list — only the `value` setter (which keys on
        value) is affected by duplicates.
        """
        self._value_by_text: dict[str, Any] = {}
        self._text_by_value: dict[Any, str] = {}
        for rec in self._records:
            display = self._record_display(rec)
            self._value_by_text.setdefault(display, rec.value)
            try:
                self._text_by_value.setdefault(rec.value, display)
            except TypeError:
                pass  # unhashable value — no reverse map; popup selection still works

    def _on_locale_changed_refresh(self, _event=None) -> None:
        """Re-translate the displayed label on a live locale change.

        Maps the currently-shown text back to its option value under the OLD
        maps, rebuilds the maps with the new translations, then re-displays that
        option's new label — only when it actually changed. A custom/typed value
        (one not backed by an option, e.g. a `TimeEntry` interval) is left
        untouched, so nothing is reformatted or re-emitted for it.
        """
        current_text = self.entry_widget.get()
        value = self._value_by_text.get(current_text) if current_text else None
        self._rebuild_option_maps()
        if value is None:
            return
        new_display = self._text_by_value.get(value, current_text)
        if new_display != current_text:
            self._set_display_text_silently(new_display)

    def _set_display_text_silently(self, text: str) -> None:
        """Replace the entry's displayed text without emitting `<<Change>>`."""
        is_readonly = self.entry_widget.instate(['readonly'])
        if is_readonly:
            self.entry_widget.state(['!readonly'])
        # Field's value setter is programmatic (no emit); display-only here.
        Field.value.fset(self, text)
        if is_readonly:
            self.entry_widget.state(['readonly'])

    def _resolve_display(self, value: Any) -> Any:
        """Map a value-space value to what the entry should hold.

        The entry owns the raw value <-> display text mapping (via
        `value_format`); the option map only kicks in to decouple an option's
        display text from its value:

        - None/empty -> the value itself (the entry clears).
        - A decoupled option (its text differs from its value) -> the option's
          display text, which the entry shows verbatim.
        - A known plain option, a custom value, or a typed value (e.g. a
          `datetime.time`) -> the value itself, so the entry's `value_format`
          parses/formats it.
        - An unknown value, when `strict_value` is set and custom values are
          off -> raises `ValueError`.
        """
        if value is None or value == "":
            return value
        try:
            if value in self._text_by_value:
                text = self._text_by_value[value]
                return text if text != value else value
        except TypeError:
            pass
        if self._strict_value and not self._allow_custom_values:
            raise ValueError(f"{value!r} is not one of the options")
        return value

    def _on_dropdown_click(self):
        """Handle dropdown button click by focusing entry then showing popup."""
        self.entry_widget.focus_set()
        self._show_selection_options()

    def _bind_readonly_selection_on_click(self):
        """Bind entry click to show popup when in readonly mode."""
        self.entry_widget.configure(cursor="hand2")
        self.entry_widget.bind('<Button-1>', lambda _: self.after_idle(self._show_selection_options), add='+')

    def _show_selection_options(self):
        """Create and display the popup list of selectable items."""
        if not self._records or self._popup_open:
            return
        if self.entry_widget.instate(['disabled']):
            return

        self._popup_open = True
        self.update_idletasks()

        # Create popup toplevel
        toplevel = self._create_popup_toplevel()

        # Create tracking variables for popup state
        popup_state = {
            'item_was_selected': False,
            'popup_closed': False,
            'first_filtered_item': None,
            'entry_focus_handler': None,
            'key_bindings': [],
            # Set once the rows exist — grouping can reorder them, so the
            # initial highlight is computed against render order (see below).
            'highlighted_index': 0,
        }

        # Setup close handler
        def close_popup(event=None):
            self._close_popup(toplevel, popup_state)

        self._popup_state = popup_state

        # Create popup content frame with items
        self._popup_frame = self._create_popup_frame(toplevel, popup_state)
        popup_state['highlighted_index'] = self._initial_highlight_index()

        # Shrink popup to fit content (still withdrawn — resize is invisible)
        self._fit_popup_height(toplevel)

        # Setup event bindings based on mode
        self._setup_popup_bindings(toplevel, popup_state, close_popup)

        # Show popup and set focus
        toplevel.deiconify()
        toplevel.lift()

        # Scroll to the selected item.  Two after_idle calls are needed: the first
        # lets Tkinter process the deiconify/pack events; the second runs once the
        # canvas has finished computing button positions so winfo_y() is accurate.
        idx = popup_state['highlighted_index']
        self.after_idle(lambda: self.after_idle(
            lambda: self._update_highlight(popup_state, idx)
        ))

        if self._search_enabled:
            self.entry_widget.focus_force()
            self.entry_widget.icursor('end')
        else:
            toplevel.focus_force()

    def _compute_popup_position(self, height: int) -> tuple[int, int, int]:
        """Return (x, y, width) for a popup of the given height.

        Flips above the entry when there isn't enough room below — matches
        Tk's combobox PlacePopdown behavior.
        """
        x = self.winfo_rootx() + (1 if self._search_enabled else 3)
        gap_below = 8 if self._search_enabled else 5
        gap_above = 4 if self._search_enabled else 1
        entry_top = self.entry_widget.winfo_rooty()
        entry_bottom = entry_top + self.entry_widget.winfo_height()
        # Clamp to a sane minimum so opening the popup before the field has been
        # laid out (winfo_width() == 1) can't produce a negative geometry.
        width = max(self.winfo_width() - (2 if self._search_enabled else 6), 1)
        screen_h = self.winfo_screenheight()
        if entry_bottom + gap_below + height > screen_h and entry_top - gap_above - height >= 0:
            y = entry_top - gap_above - height
        else:
            y = entry_bottom + gap_below
        return x, y, width

    def _popup_max_height(self, item_h: int = None) -> int:
        """Maximum popup height in px before it scrolls.

        `max_visible_items` (when set) caps the popup at roughly that many option
        rows — `n * row_height` plus a little chrome overhead. Before any row
        exists a nominal row height is assumed; `_fit_popup_height` recomputes
        with the measured height. Falls back to the built-in `_POPUP_MAX_HEIGHT`.
        """
        if self._max_visible_items:
            return self._max_visible_items * (item_h or 30) + 8
        return self._POPUP_MAX_HEIGHT

    def _create_popup_toplevel(self):
        """Create the popup toplevel window (withdrawn, provisional max-height size)."""
        max_h = self._popup_max_height()
        x, y, width = self._compute_popup_position(max_h)

        # The base_window.py warning about overrideredirect on Aqua applies
        # to full app windows that combine it with grab/transient semantics;
        # this popup uses neither (it dismisses via a root <Button-1>
        # binding), so overrideredirect is safe here and matches Tk's own
        # ttk::combobox::PlacePopdown approach for Mac popdowns.
        toplevel = Toplevel(self)
        toplevel.withdraw()
        toplevel.overrideredirect(True)
        toplevel.attributes('-topmost', True)
        toplevel.minsize(width, 0)
        toplevel.maxsize(width * 2, max_h)
        toplevel.geometry(f"{width}x{max_h}+{x}+{y}")
        return toplevel

    def _fit_popup_height(self, toplevel):
        """Shrink the popup to fit its content, up to the max popup height.

        Called after the popup frame is built but before deiconify, so the
        window is still withdrawn and the resize is invisible.
        """
        toplevel.update_idletasks()

        item_h = self._item_labels[0].winfo_reqheight() if self._item_labels else 32
        # Measure the packed content directly so group headers (which are not in
        # _item_labels) are included; fall back to a per-row estimate.
        if self._popup_inner is not None and self._popup_inner.winfo_exists():
            self._popup_inner.update_idletasks()
            content_h = self._popup_inner.winfo_reqheight() + 8
        else:
            content_h = len(self._item_labels) * item_h + 8
        # 8px overhead: outer_frame border (2px each side) + padding (3px each side)
        cap = self._popup_max_height(item_h)
        actual_h = max(min(content_h, cap), item_h)

        x, y, width = self._compute_popup_position(actual_h)
        toplevel.maxsize(width * 2, max(cap, actual_h))
        toplevel.geometry(f"{width}x{actual_h}+{x}+{y}")

    def _create_popup_frame(self, toplevel, popup_state):
        """Create popup frame with scrollable item list."""
        # Outer frame with border and padding — match the entry's input
        # surface so the popup fill blends with the field background.
        outer_frame = Frame(toplevel, padding=3, show_border=True, surface='content')
        outer_frame.pack(fill='both', expand=True)

        # Create scrollview inside the outer frame
        scrollview = ScrollView(
            outer_frame,
            scroll_direction='vertical',
            scrollbar_visibility='always',
            scrollbar_variant='thin',
            surface='content',
        )
        scrollview.pack(fill='both', expand=True)

        # Create inner frame for items
        inner_frame = Frame(scrollview)
        scrollview.add(inner_frame)
        self._popup_inner = inner_frame

        # Make inner frame fill the canvas width
        def on_canvas_configure(event):
            scrollview.canvas.itemconfig(scrollview._window_id, width=event.width - 2)
        scrollview.canvas.bind('<Configure>', on_canvas_configure, add='+')

        # Expand scrollregion to include vertical padding so content doesn't clip borders
        def on_inner_frame_configure(event):
            bbox = scrollview.canvas.bbox('all')
            if bbox:
                x0, y0, x1, y1 = bbox
                padding_y = 1
                scrollview.canvas.configure(scrollregion=(x0, y0 - padding_y, x1, y1 + padding_y))
        inner_frame.bind('<Configure>', on_inner_frame_configure, add='+')

        self._item_labels = []
        self._group_headers = []
        self._popup_rows = []
        current_text = self.entry_widget.get()

        # Get accent from Field's _accent attribute, fallback to primary if None
        accent = getattr(self, '_accent', None) or 'primary'

        def pack_row(row, **kw):
            # Pack a popup row and remember its pack options, so search re-packs
            # (which forget then re-pack) preserve per-row spacing.
            kw.setdefault('fill', 'x')
            row._pack_kw = kw
            row.pack(**kw)
            self._popup_rows.append(row)

        # Cluster rows by the grouping field (a no-op single bucket when
        # group_by is None). A named group gets a bold header, preceded by a
        # separator except at the very top. Option buttons keep their
        # render-order slot in _item_labels so the existing nav/search/highlight
        # indexing is unchanged. Headers and separators are non-selectable.
        i = 0
        for group_label, recs in cluster_records(self._records, self._group_by):
            header_widgets = []
            if group_label is not None:
                if self._popup_rows:  # not the first row — divide from above
                    sep = Separator(inner_frame, orient='horizontal')
                    sep._is_separator = True
                    pack_row(sep, pady=(5, 2))
                    header_widgets.append(sep)
                header = self._create_group_header(inner_frame, group_label)
                pack_row(header)
                header_widgets.append(header)
            group_buttons = []

            for rec in recs:
                icon, disabled = option_display(rec)
                # Translate the row label once (honoring a per-option localize
                # key); pass localize=False so the Button shows it verbatim and
                # the entry/search/value all agree on the same display text.
                display = self._record_display(rec)
                btn_kwargs = {}
                if icon is not None:
                    btn_kwargs['icon'] = icon
                    if option_is_icon_only(rec):
                        btn_kwargs['icon_only'] = True
                btn = Button(
                    inner_frame,
                    text=display,
                    localize=False,
                    accent=accent,
                    variant='selectbox_item',
                    takefocus=False,
                    command=lambda v=rec.value: self._on_item_click(v, toplevel, popup_state),
                    **btn_kwargs,
                )
                pack_row(btn)

                # Store the option's value (for selection) and display text (for
                # filtering — search matches what the user sees).
                btn._item_value = rec.value
                btn._item_text = display
                btn._item_index = i
                btn._item_disabled = disabled
                # When highlighted, scroll to reveal the group's header/separator
                # above the button (not just the button) so the section heading
                # stays on screen.
                btn._reveal_top = header_widgets[0] if header_widgets else btn
                i += 1

                # A disabled option is dimmed and cannot be chosen — clicking it
                # does nothing (ttk blocks the command) and it is skipped by the
                # keyboard navigation and search auto-select below.
                if disabled:
                    btn.state(['disabled'])
                # Apply selected state if this row matches the displayed text
                if display == current_text:
                    btn.state(['selected'])

                self._item_labels.append(btn)
                group_buttons.append(btn)

            if header_widgets:
                self._group_headers.append((header_widgets, group_buttons))

        return scrollview

    def _repack_popup_rows(self, is_visible):
        """Re-pack popup rows in canonical render order, hiding filtered ones.

        Forgets every row then re-packs the visible ones in their original
        order, so a row that reappears after being filtered out lands back in
        its correct slot (rather than at the end, which a bare `pack()` of a
        previously-forgotten widget would do). The forget/pack pass is coalesced
        at idle, so there is no visible flicker.

        Args:
            is_visible: Predicate called with each row widget; truthy keeps it.
        """
        for row in self._popup_rows:
            row.pack_forget()
        seen_content = False
        for row in self._popup_rows:
            if not is_visible(row):
                continue
            is_sep = getattr(row, '_is_separator', False)
            if is_sep and not seen_content:
                continue  # a divider with nothing visible above it — drop it
            row.pack(**getattr(row, '_pack_kw', {'fill': 'x'}))
            seen_content = seen_content or not is_sep

    def _create_group_header(self, parent, text):
        """Create a non-selectable group-header label for the popup.

        Rendered in the option rows' font, bold, and verbatim — the group value
        is never transformed, so `selection`/`group_by` keep the original text.
        """
        return Label(parent, text=str(text), font='body[bold]', anchor='w', padding=(8, 4, 4, 3))

    def _initial_highlight_index(self) -> int:
        """Render-order index of the row to highlight when the popup opens.

        The currently-selected option when it is present and enabled, otherwise
        the first enabled option. Computed against `_item_labels` (render order)
        so it stays correct when grouping reorders rows.
        """
        selected = self.value
        first_enabled = None
        for idx, btn in enumerate(self._item_labels):
            if getattr(btn, '_item_disabled', False):
                continue
            if first_enabled is None:
                first_enabled = idx
            if btn._item_value == selected:
                return idx
        return first_enabled if first_enabled is not None else 0

    def _on_item_click(self, value, toplevel, popup_state):
        """Handle click on item."""
        popup_state['item_was_selected'] = True
        self._set_selected_value(value, toplevel, popup_state)

    def _first_enabled_index(self) -> int:
        """Index of the first non-disabled option, or 0 if all are disabled."""
        return next(
            (i for i, rec in enumerate(self._records) if not option_display(rec)[1]),
            0,
        )

    def _step_highlight(self, popup_state, step):
        """Move the highlight by `step`, skipping disabled rows.

        Stops at the first non-disabled visible row in the given direction;
        keeps the current highlight when the edge is reached.
        """
        visible_buttons = [btn for btn in self._item_labels if btn.winfo_manager()]
        if not visible_buttons:
            return
        idx = popup_state['highlighted_index']
        n = len(visible_buttons)
        while True:
            idx += step
            if idx < 0 or idx >= n:
                return  # reached the edge — keep the current highlight
            if not getattr(visible_buttons[idx], '_item_disabled', False):
                self._update_highlight(popup_state, idx)
                return

    def _update_highlight(self, popup_state, new_index):
        """Update the highlighted item in the popup."""
        visible_buttons = [btn for btn in self._item_labels if btn.winfo_manager()]
        if not visible_buttons:
            return

        # Clamp index to valid range
        new_index = max(0, min(new_index, len(visible_buttons) - 1))
        old_index = popup_state['highlighted_index']

        # Remove highlight from old button
        if 0 <= old_index < len(visible_buttons):
            visible_buttons[old_index].state(['!selected'])

        # Add highlight to new button
        visible_buttons[new_index].state(['selected'])
        popup_state['highlighted_index'] = new_index

        # Scroll to make highlighted item visible
        btn = visible_buttons[new_index]
        if self._popup_frame and self._popup_frame.winfo_exists():
            self._popup_frame.canvas.update_idletasks()
            # Get button position relative to canvas
            btn_y = btn.winfo_y()
            btn_height = btn.winfo_height()
            canvas_height = self._popup_frame.canvas.winfo_height()

            # Scroll if needed
            scroll_top = self._popup_frame.canvas.canvasy(0)
            scroll_bottom = scroll_top + canvas_height

            # When scrolling up, reveal the group's header/separator above the
            # button (not just the button) so the section heading stays visible.
            reveal = getattr(btn, '_reveal_top', None) or btn
            reveal_y = reveal.winfo_y()

            if reveal_y < scroll_top:
                self._popup_frame.canvas.yview_moveto(reveal_y / self._popup_frame.canvas.bbox('all')[3])
            elif btn_y + btn_height > scroll_bottom:
                target = (btn_y + btn_height - canvas_height) / self._popup_frame.canvas.bbox('all')[3]
                self._popup_frame.canvas.yview_moveto(target)

    def _setup_popup_bindings(self, toplevel, popup_state, close_popup):
        """Setup all event bindings for the popup."""
        # Escape always closes
        toplevel.bind("<Escape>", close_popup)

        # Arrow key navigation (skips disabled rows)
        def on_arrow_down(event):
            self._step_highlight(popup_state, 1)
            return 'break'

        def on_arrow_up(event):
            self._step_highlight(popup_state, -1)
            return 'break'

        def on_enter(event):
            visible_buttons = [btn for btn in self._item_labels if btn.winfo_manager()]
            idx = popup_state['highlighted_index']
            if 0 <= idx < len(visible_buttons):
                btn = visible_buttons[idx]
                if getattr(btn, '_item_disabled', False):
                    return 'break'  # a disabled row can't be chosen
                popup_state['item_was_selected'] = True
                self._set_selected_value(btn._item_value, toplevel, popup_state)
            return 'break'

        toplevel.bind("<Down>", on_arrow_down)
        toplevel.bind("<Up>", on_arrow_up)
        toplevel.bind("<Return>", on_enter)

        # Also bind to entry widget for search mode
        if self._search_enabled:
            self._setup_search_bindings(toplevel, popup_state, close_popup)
            entry_down = self.entry_widget.bind('<Down>', on_arrow_down, add='+')
            entry_up = self.entry_widget.bind('<Up>', on_arrow_up, add='+')
            entry_enter = self.entry_widget.bind('<Return>', on_enter, add='+')
            popup_state['key_bindings'].append(('<Down>', entry_down))
            popup_state['key_bindings'].append(('<Up>', entry_up))
            popup_state['key_bindings'].append(('<Return>', entry_enter))
        else:
            toplevel.bind("<FocusOut>", close_popup)

        # Initial highlight state is applied after deiconify (see _show_selection_options)

    def _apply_search_filter(self, popup_state):
        """Filter the popup rows to those matching the entry text.

        Shows option buttons whose display text contains the (case-insensitive)
        search text; a group's header and separator show only while the group
        has a visible option. The first enabled match drives the auto-select
        target and the reset highlight. A no-op when the text is unchanged or the
        popup is gone.
        """
        if popup_state['popup_closed'] or not self._popup_frame or not self._popup_frame.winfo_exists():
            return

        search_text = self.entry_widget.get().lower()

        # Skip if search text hasn't changed (e.g., arrow key release)
        if search_text == popup_state['last_search_text']:
            return
        popup_state['last_search_text'] = search_text

        # Decide which option buttons match — on the visible TEXT. The first
        # ENABLED match drives auto-select + the reset highlight.
        match = {}
        first_visible = None
        for btn in self._item_labels:
            ok = search_text in btn._item_text.lower()
            match[btn] = ok
            if ok and first_visible is None and not getattr(btn, '_item_disabled', False):
                first_visible = btn

        # A group's header + separator show only while it has a visible option.
        header_visible = {}
        for header_widgets, group_buttons in self._group_headers:
            vis = any(match.get(b, False) for b in group_buttons)
            for w in header_widgets:
                header_visible[w] = vis
        self._repack_popup_rows(
            lambda row: match.get(row, header_visible.get(row, True))
        )

        # Track first filtered item for auto-select (value-space)
        popup_state['first_filtered_item'] = first_visible._item_value if first_visible else None

        # Reset highlight to the first enabled visible item
        visible_buttons = [b for b in self._item_labels if b.winfo_manager()]
        target = next(
            (i for i, b in enumerate(visible_buttons)
             if not getattr(b, '_item_disabled', False)),
            0,
        )
        self._update_highlight(popup_state, target)

    def _setup_search_bindings(self, toplevel, popup_state, close_popup):
        """Setup search-specific event bindings."""
        # Initialize first filtered item (stored in value-space); skip disabled
        # so an auto-select on close never lands on a non-selectable option.
        enabled = [rec for rec in self._records if not option_display(rec)[1]]
        if enabled:
            popup_state['first_filtered_item'] = enabled[0].value
        popup_state['last_search_text'] = self.entry_widget.get().lower()

        # Bind KeyRelease for filtering (delegates to the testable method)
        keyrelease_binding = self.entry_widget.bind(
            '<KeyRelease>', lambda e: self._apply_search_filter(popup_state), add='+'
        )
        popup_state['key_bindings'].append(('<KeyRelease>', keyrelease_binding))

        # Bind Tab to select highlighted item
        def on_tab(event):
            if popup_state['popup_closed']:
                return
            visible_buttons = [btn for btn in self._item_labels if btn.winfo_manager()]
            idx = popup_state['highlighted_index']
            if 0 <= idx < len(visible_buttons):
                btn = visible_buttons[idx]
                if getattr(btn, '_item_disabled', False):
                    return 'break'  # a disabled row can't be chosen
                popup_state['item_was_selected'] = True
                self._set_selected_value(btn._item_value, toplevel, popup_state)
            return 'break'

        tab_binding = self.entry_widget.bind('<Tab>', on_tab)
        popup_state['key_bindings'].append(('<Tab>', tab_binding))

        # Setup click-outside detection
        def on_root_click(event):
            x, y = event.x_root, event.y_root

            # Check if click is inside entry widget
            ex, ey = self.entry_widget.winfo_rootx(), self.entry_widget.winfo_rooty()
            ew, eh = self.entry_widget.winfo_width(), self.entry_widget.winfo_height()
            if ex <= x <= ex + ew and ey <= y <= ey + eh:
                return

            # Check if click is inside toplevel
            if toplevel.winfo_exists():
                tx, ty = toplevel.winfo_rootx(), toplevel.winfo_rooty()
                tw, th = toplevel.winfo_width(), toplevel.winfo_height()
                if tx <= x <= tx + tw and ty <= y <= ty + th:
                    return

            close_popup()

        def bind_click():
            if popup_state['popup_closed']:
                return
            root = self.winfo_toplevel()
            bind_id = root.bind('<Button-1>', on_root_click, add='+')
            popup_state['entry_focus_handler'] = bind_id

        self.after(100, bind_click)

    def _close_popup(self, toplevel, popup_state):
        """Close the popup and cleanup bindings."""
        if popup_state['popup_closed']:
            return

        popup_state['popup_closed'] = True
        self._popup_open = False

        # Unbind handlers
        if popup_state['entry_focus_handler'] is not None and self._search_enabled:
            root = self.winfo_toplevel()
            root.unbind('<Button-1>', popup_state['entry_focus_handler'])

        # Unbind key bindings
        for sequence, funcid in popup_state['key_bindings']:
            self.entry_widget.unbind(sequence, funcid)

        # Destroy toplevel
        if toplevel.winfo_exists():
            toplevel.destroy()

        # Clean up popup references
        self._popup_frame = None
        self._popup_inner = None
        self._item_labels = []
        self._group_headers = []
        self._popup_rows = []
        self._popup_state = None

        # Handle value selection for search mode without custom values
        if self._search_enabled and not self._allow_custom_values:
            if not popup_state['item_was_selected']:
                if popup_state['first_filtered_item'] is not None:
                    self._last_selected_value = popup_state['first_filtered_item']
                    self.value = popup_state['first_filtered_item']

    def _set_selected_value(self, selected_value, toplevel, popup_state):
        """Set the selected value and close the popup."""
        if selected_value is None:
            return

        self._last_selected_value = selected_value
        self.value = selected_value
        self._close_popup(toplevel, popup_state)

    @configure_delegate('items')
    def _delegate_items(self, value: list[Option] = None):
        """Get the normalized option records, or set new options."""
        if value is None:
            return list(self._records)
        else:
            self._records = normalize_options(value)
            self._rebuild_option_maps()
            # Reconcile the displayed selection: if its text is no longer an
            # option (and custom values aren't allowed), clear it.
            if self.entry_widget.get() not in self._value_by_text and not self._allow_custom_values:
                self.value = None
        return None

    @configure_delegate('allow_custom_values')
    def _delegate_allow_custom_values(self, value: bool = None):
        """Get or set whether free-form text entry is allowed."""
        if value is None:
            return self._allow_custom_values
        else:
            self._allow_custom_values = value
            if value or self._search_enabled:
                self.entry_widget.state(['!readonly'])
            else:
                self.readonly(True)
        return None

    @configure_delegate('enable_search')
    def _delegate_enable_search(self, value: bool = None):
        """Get or set whether search filtering is enabled."""
        if value is None:
            return self._search_enabled
        else:
            self._search_enabled = value
            if value or self._allow_custom_values:
                self.entry_widget.state(['!readonly'])
            else:
                self.readonly(True)
        return None

    @configure_delegate('group_by')
    def _delegate_group_by(self, value=None):
        """Get or set the option field the popup clusters rows under.

        The change takes effect the next time the popup opens (it is rebuilt on
        each open). Following the configure-delegate convention, `None` reads the
        current field; disable grouping at runtime by setting it to `''`.
        """
        if value is None:
            return self._group_by
        self._group_by = value or None
        return None

    @configure_delegate('max_visible_items')
    def _delegate_max_visible_items(self, value=None):
        """Get or set the approximate visible-row cap before the popup scrolls.

        The change takes effect the next time the popup opens. Following the
        configure-delegate convention, `None` reads the current value; set it to
        `0` to restore the built-in default cap.
        """
        if value is None:
            return self._max_visible_items
        self._max_visible_items = value or None
        return None

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        if value is None:
            return self.value
        self.value = value
        return None

    @property
    def selected_index(self) -> int:
        """Get or set the selected index.

        Returns -1 if nothing is selected (the displayed text matches no
        option). Setting to -1 or None clears the selection.
        """
        text = self.entry_widget.get()
        for i, rec in enumerate(self._records):
            if self._record_display(rec) == text:
                return i
        return -1

    @selected_index.setter
    def selected_index(self, index):
        if index is None or index == -1:
            self.value = None
        elif 0 <= index < len(self._records):
            self.value = self._records[index].value
        else:
            raise IndexError(f"index {index} out of range for {len(self._records)} options")

    @property
    def text(self) -> str:
        """The current display text shown in the field (the formatted string)."""
        return self.entry_widget.get()

    @property
    def selection(self) -> dict | None:
        """The selected option as a full record dict (the data bag), or None.

        Returns the matching option's `{text, value, ...extras}`; None when
        nothing is selected or the current value is a custom/off-list one (not
        one of the options).
        """
        value = self.value
        if value is None:
            return None
        for rec in self._records:
            if rec.value == value:
                return record_to_dict(rec)
        return None

    @property
    def value(self):
        """The selected value, or None when the field is empty.

        For a decoupled option (its display text differs from its value) this
        returns the option's value. Otherwise it returns the entry's own raw
        value, so `value_format` parsing — e.g. TimeField's `datetime.time` —
        is preserved.
        """
        text = self.entry_widget.get()
        if text == "":
            return None
        if text in self._value_by_text and self._value_by_text[text] != text:
            return self._value_by_text[text]
        return Field.value.fget(self)

    @value.setter
    def value(self, value):
        """Select `value`, updating the displayed text and emitting `<<Change>>`.

        A decoupled option shows its text; a plain/typed/custom value is handed
        to the entry, which owns the raw value <-> text formatting. An unknown
        value raises `ValueError` when `strict_value` is set and custom values
        are off.
        """
        prev_value = self.value
        display = self._resolve_display(value)
        is_readonly = self.entry_widget.instate(['readonly'])
        if is_readonly:
            self.entry_widget.state(['!readonly'])
        if display is None or display == "":
            # The entry part's value() setter doesn't reliably clear the field;
            # empty it directly.
            self.entry_widget.delete(0, 'end')
        else:
            # The entry owns raw<->text; setting its value is programmatic (no emit).
            Field.value.fset(self, display)
        if is_readonly:
            self.entry_widget.state(['readonly'])
        new_value = self.value
        if new_value != prev_value:
            self.entry_widget._prev_changed_value = new_value
            if not getattr(self, "_suppress_changed_event", False):
                self.entry_widget.event_generate(
                    '<<Change>>',
                    data=ChangeEvent(
                        value=new_value,
                        prev_value=prev_value,
                        text=self.entry_widget.get(),
                    ),
                    when="tail"
                )

