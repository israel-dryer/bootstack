"""ListView widget for displaying large lists with virtual scrolling."""

from tkinter import TclError
from typing import Any, Callable, Literal

from bootstack.datasource import MemoryDataSource, DataSourceProtocol
from bootstack.widgets.composites.list.listitem import ListItem
from bootstack.widgets.primitives.frame import Frame
from bootstack.widgets.primitives.scrollbar import Scrollbar
from bootstack.widgets.mixins import configure_delegate

# Constants
VISIBLE_ROWS = 20
ROW_HEIGHT = 40
OVERSCAN_ROWS = 2
EMPTY = {"__empty__": True, "id": "__empty__"}



class ListView(Frame):
    """A virtual scrolling list widget for efficiently displaying large datasets.

    ListView uses virtual scrolling to render only visible items, allowing it to
    handle thousands of records efficiently. It supports multiple selection modes,
    item deletion, drag and drop, and custom styling.

    The widget works with either a simple list/dict data or a custom DataSource
    implementation for more complex scenarios (database, API, etc.).

    !!! note "Events"
        - `<<SelectionChange>>`: Fired when selection state changes. `event.data = None` (use `get_selected()` to get current selection)
        - `<<ItemDelete>>`: Fired when an item is deleted. `event.data = dict` (the deleted record; contains at least `id`)
        - `<<ItemDeleteFail>>`: Fired when item deletion fails. `event.data = dict` (the record plus an `error: str` key)
        - `<<ItemInsert>>`: Fired when a new item is inserted. `event.data = dict` (the new record, with `id` populated)
        - `<<ItemUpdate>>`: Fired when an item is updated. `event.data = dict` (the merged record, with `id`)
        - `<<ItemClick>>`: Fired when an item is clicked. `event.data = dict` (the record, with `selected`, `focused`, `item_index` injected)
        - `<<ItemDragStart>>`: Fired when a drag begins. `event.data = dict` (the record)
        - `<<ItemDrag>>`: Fired during a drag. `event.data = dict` (record plus `source_index`, `target_index`, `y_current`)
        - `<<ItemDragEnd>>`: Fired when a drag ends. `event.data = dict` (record plus `source_index`, `target_index`, `moved`, `y_start`, `y_end`)
    """

    def __init__(
            self,
            master=None,
            items: list = None,
            datasource: DataSourceProtocol = None,
            _row_factory: Callable = None,
            selection_mode: Literal['none', 'single', 'multi'] = 'none',
            show_selection_controls: bool = False,
            show_chevron: bool = False,
            enable_removing: bool = False,
            enable_dragging: bool = False,
            striped: bool = False,
            striped_background: str = 'background[+1]',
            show_separator: bool = True,
            scrollbar_visibility: Literal['always', 'never'] = 'always',
            enable_focus: bool = True,
            enable_hover: bool = True,
            select_on_click: bool = None,
            density: Literal['default', 'compact'] = 'default',
            **kwargs
    ):
        """Initialize a ListView widget.

        Args:
            master: Parent widget.
            items: List of items or dicts to display (alternative to `datasource`).
            datasource: DataSource implementation for data access.
            selection_mode: Selection mode (`none`, `single`, `multi`).
            show_selection_controls: Show checkboxes/radio buttons for selection.
            show_chevron: Show chevron indicators on items.
            enable_removing: Allow items to be removed; shows remove button on items.
            enable_dragging: Allow row dragging; shows drag handle on items.
            striped: Whether to show alternating row colors.
            striped_background: The background color for striped rows.
            show_separator: Show separator line between items.
            scrollbar_visibility: Scrollbar visibility - 'always' to show scrollbar,
                'never' to hide (mousewheel only). Defaults to 'always'.
            enable_focus: Whether items can receive keyboard focus.
            enable_hover: Whether items show hover state.
            select_on_click: Whether clicking an item selects it. Defaults to True when
                selection_mode is 'single' or 'multi', False otherwise. Can be explicitly
                set to override the default behavior.
            density: Visual density ('default' or 'compact'). Defaults to 'default'.
            **kwargs: Additional keyword arguments forwarded to `Frame`.
        """
        # Capture user-provided accent for row propagation and the drag indicator.
        # super().__init__ runs through the bootstyle wrapper which sets self._accent
        # to whatever's in kwargs (None if absent), so we re-assert with a 'primary'
        # fallback after super() completes.
        _user_accent = kwargs.get('accent')

        super().__init__(master, variant='container', ttk_class='ListView.TFrame', **kwargs)

        self._accent = _user_accent or 'primary'

        # Cache the windowing system so scroll bindings can dispatch
        # platform-correctly: Aqua/Win send <MouseWheel>, X11 sends
        # <Button-4>/<Button-5>.
        self.winsys = self.tk.call('tk', 'windowingsystem')

        # Configuration
        self._selection_mode = selection_mode
        self._show_selection_controls = show_selection_controls
        self._show_chevron = show_chevron
        self._enable_removing = enable_removing
        self._enable_dragging = enable_dragging
        self._show_separator = show_separator
        self._scrollbar_visibility = scrollbar_visibility
        self._select_on_click = select_on_click
        self._enable_focus = enable_focus
        self._enable_hover = enable_hover
        self._striped = striped
        self._striped_background = striped_background
        self._density = density

        # Virtual scrolling state
        self._start_index = 0
        self._prev_start_index = 0
        self._visible_rows = VISIBLE_ROWS
        self._row_height = ROW_HEIGHT
        self._page_size = VISIBLE_ROWS + OVERSCAN_ROWS

        # Data source
        if datasource:
            self._datasource = datasource
        elif items:
            self._datasource = MemoryDataSource(page_size=self._page_size).set_data(items)
        else:
            self._datasource = MemoryDataSource(page_size=self._page_size).set_data([])

        self._rows: list[ListItem] = []
        self._focused_record_id = None
        self._drag_state: dict | None = None
        self._drag_indicator: Frame | None = None
        self._drag_scroll_counter = 0
        self._mousewheel_bound_widgets: set = set()  # Track bound widgets to avoid cycles

        # Row factory
        self._row_factory = _row_factory or self._default_row_factory

        # Create container frame for list items
        self._container = Frame(self, variant='container', ttk_class='ListView.TFrame')
        self._container.pack(side='left', fill='both', expand=True)

        # Create scrollbar
        self._scrollbar = Scrollbar(self, orient='vertical', command=self._on_scroll)
        if self._scrollbar_visibility == 'always':
            self._scrollbar.pack(side='right', fill='y')

        # Create row pool
        self._ensure_row_pool(self._page_size)

        # Bind events
        self.bind('<Configure>', self._on_resize, add='+')
        self._bind_scroll_events(self)
        self._bind_scroll_events(self._container)

        # Bind ListItem events
        self._container.bind('<<ItemSelecting>>', self._on_item_selecting, add='+')
        self._container.bind('<<ItemRemoving>>', self._on_item_removing, add='+')
        self._container.bind('<<ItemFocus>>', self._on_item_focused, add='+')
        self._container.bind('<<ItemClick>>', self._on_item_click, add='+')
        self._container.bind('<<ItemDragStart>>', self._on_item_drag_start, add='+')
        self._container.bind('<<ItemDrag>>', self._on_item_dragging, add='+')
        self._container.bind('<<ItemDragEnd>>', self._on_item_drag_end, add='+')

        # Bind keyboard navigation
        self.bind('<Down>', self._on_arrow_down, add='+')
        self.bind('<Up>', self._on_arrow_up, add='+')
        self._container.bind('<Down>', self._on_arrow_down, add='+')
        self._container.bind('<Up>', self._on_arrow_up, add='+')

        # Initial update
        self.after(10, self._remeasure_and_relayout)

    @configure_delegate('selection_mode')
    def _delegate_selection_mode(self, value=None):
        """Get or set the selection mode.

        Args:
            value: If provided, sets the selection mode to 'none', 'single', or 'multi'.
                If None, returns the current selection mode.

        Returns:
            Current selection mode when called without arguments.
        """
        if value is None:
            return self._selection_mode
        else:
            self._selection_mode = value
            # Recreate row pool to apply new selection mode
            self._ensure_row_pool(self._page_size)
            self._update_rows()
        return None

    @configure_delegate('scrollbar_visibility')
    def _delegate_scrollbar_visibility(self, value=None):
        """Get or set scrollbar visibility.

        Args:
            value: If provided ('always' or 'never'), shows or hides the scrollbar.
                If None, returns current visibility setting.

        Returns:
            Current scrollbar_visibility value when called without arguments.
        """
        if value is None:
            return self._scrollbar_visibility
        else:
            old_value = self._scrollbar_visibility
            self._scrollbar_visibility = value
            if old_value != self._scrollbar_visibility:
                if self._scrollbar_visibility == 'always':
                    self._scrollbar.pack(side='right', fill='y')
                else:
                    self._scrollbar.pack_forget()
        return None

    @configure_delegate('striped')
    def _delegate_striped(self, value=None):
        """Get or set striped mode.

        Args:
            value: If provided, enables or disables striped rows.
                If None, returns the current mode.

        Returns:
            Current striped value when called without arguments.
        """
        if value is None:
            return self._striped
        else:
            self._striped = bool(value)
            # Reapply surface colors to all rows
            for i, row in enumerate(self._rows):
                self._apply_widget_surface(row, i)
        return None

    @configure_delegate('striped_background')
    def _delegate_striped_background(self, value=None):
        """Get or set striped row background color.

        Args:
            value: If provided, sets the striped row background color.
                If None, returns the current color.

        Returns:
            Current striped_background when called without arguments.
        """
        if value is None:
            return self._striped_background
        else:
            self._striped_background = value
            # Reapply surface colors to all rows
            for i, row in enumerate(self._rows):
                self._apply_widget_surface(row, i)
        return None

    @staticmethod
    def _default_row_factory(master, **kwargs):
        """Create a default `ListItem`.

        Args:
            master: Parent widget.
            **kwargs: Keyword arguments for `ListItem`.

        Returns:
            A new `ListItem` instance.
        """
        return ListItem(master, **kwargs)

    def _ensure_row_pool(self, needed: int):
        """Create/destroy `ListItem` widgets to match pool size.

        Args:
            needed: Desired number of row widgets.
        """
        while len(self._rows) < needed:
            # Build kwargs for row factory (using item-level names)
            row_kwargs = dict(
                selection_mode=self._selection_mode,
                show_selection_controls=self._show_selection_controls,
                show_chevron=self._show_chevron,
                removable=self._enable_removing,
                draggable=self._enable_dragging,
                show_separator=self._show_separator,
                focusable=self._enable_focus,
                hoverable=self._enable_hover,
                accent=self._accent,
                density=self._density
            )

            # Only pass select_on_click if explicitly set
            if self._select_on_click is not None:
                row_kwargs['select_on_click'] = self._select_on_click

            row = self._row_factory(self._container, **row_kwargs)
            row.pack(fill='x')
            self._rows.append(row)

            # Bind keyboard navigation to each row and its children
            self._bind_arrow_keys_recursive(row)

            # Apply surface color once based on widget position
            widget_index = len(self._rows) - 1
            self._apply_widget_surface(row, widget_index)

        while len(self._rows) > needed:
            row = self._rows.pop()
            row.pack_forget()
            try:
                row.destroy()
            except TclError:
                pass

    def _clamp_indices(self):
        """Ensure `self._start_index` is within valid range."""
        total = self._datasource.total_count()
        max_start = max(0, total - self._visible_rows)
        self._start_index = max(0, min(self._start_index, max_start))

    def _update_rows(self):
        """Update visible rows with current data using row recycling for efficiency."""
        self._clamp_indices()

        # Calculate scroll distance to determine if we can use recycling
        scroll_distance = self._start_index - self._prev_start_index
        can_recycle = abs(scroll_distance) <= 3 and scroll_distance != 0

        if can_recycle:
            # Use row recycling for small scrolls
            self._recycle_rows(scroll_distance)
        else:
            # Full update for large scrolls or initial render
            self._full_update_rows()

        # Remember current position for next scroll
        self._prev_start_index = self._start_index

        # Update scrollbar
        total = max(1, self._datasource.total_count())
        first = self._start_index / total
        last = min(1.0, (self._start_index + self._visible_rows) / total)
        self._scrollbar.set(first, last)

    def _recycle_rows(self, scroll_distance: int):
        """Recycle rows by moving them from one end to the other.

        Args:
            scroll_distance: Positive for scrolling down, negative for scrolling up.
        """
        if scroll_distance > 0:
            # Scrolling down: move top rows to bottom
            for _ in range(scroll_distance):
                if not self._rows:
                    break

                # Remove top row
                top_row = self._rows.pop(0)

                # Calculate new data index
                data_index = self._start_index + len(self._rows)

                # Update data BEFORE moving widget to prevent focus tracking widget
                self._update_single_row(top_row, data_index)

                # Move to bottom
                top_row.pack_forget()
                top_row.pack(side='top', fill='x')
                self._rows.append(top_row)

        elif scroll_distance < 0:
            # Scrolling up: move bottom rows to top
            for _ in range(abs(scroll_distance)):
                if not self._rows:
                    break

                # Remove bottom row
                bottom_row = self._rows.pop()

                # Calculate new data index
                data_index = self._start_index

                # Update data BEFORE moving widget to prevent focus tracking widget
                self._update_single_row(bottom_row, data_index)

                # Move to top
                bottom_row.pack_forget()
                if self._rows:
                    bottom_row.pack(side='top', fill='x', before=self._rows[0])
                else:
                    bottom_row.pack(side='top', fill='x')
                self._rows.insert(0, bottom_row)

    def _full_update_rows(self):
        """Perform a full update of all visible rows."""
        page_data = self._datasource.get_page_from_index(self._start_index, self._page_size)

        for i, row in enumerate(self._rows):
            data_index = self._start_index + i
            if i < len(page_data):
                self._update_single_row(row, data_index, page_data[i])
            else:
                row.update_data(EMPTY)

    def _update_single_row(self, row: ListItem, data_index: int, record: dict = None):
        """Update a single row widget with data at the given index.

        Args:
            row: The ListItem widget to update.
            data_index: The data index to fetch and display.
            record: Optional pre-fetched record data. If None, will fetch from datasource.
        """
        if record is None:
            # Fetch the record from datasource
            page_data = self._datasource.get_page_from_index(data_index, 1)
            if not page_data:
                row.update_data(EMPTY)
                # Bind mousewheel after update to ensure all child widgets exist
                self._bind_mousewheel_recursive(row)
                return
            record = page_data[0]

        record = record.copy()
        record_id = record.get('id')

        # Add selection state
        if record_id is not None:
            try:
                record['selected'] = self._datasource.is_selected(record_id)
            except Exception:
                record['selected'] = False
            record['focused'] = (record_id == self._focused_record_id)
        else:
            record['selected'] = False
            record['focused'] = False

        # Add index
        record['item_index'] = data_index

        # Update the row
        row.update_data(record)

        # Bind mousewheel after update to ensure all child widgets exist
        self._bind_mousewheel_recursive(row)

    def _on_scroll(self, *args):
        """Handle scrollbar movement.

        Args:
            *args: Tkinter scrollbar arguments.
        """
        if args[0] == 'moveto':
            fraction = float(args[1])
            total = self._datasource.total_count()
            max_start = max(0, total - self._visible_rows)
            self._start_index = int(round(fraction * max_start))
        elif args[0] == 'scroll':
            amount = int(args[1])
            unit = args[2]
            # Use smaller step size for smoother scrolling
            step = max(1, self._visible_rows // 2) if unit == 'pages' else 1
            self._start_index += amount * step

        self._clamp_indices()
        self._update_rows()

    def _bind_mousewheel_recursive(self, widget):
        """Recursively bind mousewheel event to a widget and all its children.

        Only binds if the widget hasn't been bound already to avoid duplicate bindings.

        Args:
            widget: The widget to bind mousewheel event to.
        """
        # Use widget string representation as identifier
        widget_id = str(widget)

        # Only bind if we haven't already bound this widget
        if widget_id not in self._mousewheel_bound_widgets:
            self._bind_scroll_events(widget)
            self._mousewheel_bound_widgets.add(widget_id)

        try:
            for child in widget.winfo_children():
                self._bind_mousewheel_recursive(child)
        except Exception:
            pass

    def _bind_arrow_keys_recursive(self, widget):
        """Recursively bind arrow key events to a widget and all its children.

        Args:
            widget: The widget to bind arrow key events to.
        """
        widget.bind('<Down>', self._on_arrow_down, add='+')
        widget.bind('<Up>', self._on_arrow_up, add='+')

        try:
            for child in widget.winfo_children():
                self._bind_arrow_keys_recursive(child)
        except Exception:
            pass

    def _bind_scroll_events(self, widget) -> None:
        """Bind the platform-correct scroll-wheel events to `widget`.

        On Aqua/Win the event is `<MouseWheel>` with `event.delta`
        carrying direction and magnitude. On X11 there's no MouseWheel —
        scroll up is `<Button-4>` and scroll down is `<Button-5>`.
        """
        if self.winsys.lower() == 'x11':
            widget.bind('<Button-4>', self._on_mousewheel, add='+')
            widget.bind('<Button-5>', self._on_mousewheel, add='+')
        else:
            widget.bind('<MouseWheel>', self._on_mousewheel, add='+')

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling.

        Args:
            event: Tkinter mouse wheel event.
        """
        # Check if mouse is over this widget
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        if widget_under_mouse is None:
            return

        # Check if the widget under mouse is a child of this ListView
        current = widget_under_mouse
        is_child = False
        while current is not None:
            if current == self:
                is_child = True
                break
            try:
                current = current.master
            except AttributeError:
                break

        if not is_child:
            return

        # Resolve scroll direction per platform: X11 carries it in event.num
        # (4=up, 5=down) and has no event.delta; Aqua/Win use event.delta.
        if self.winsys.lower() == 'x11':
            delta = -1 if getattr(event, 'num', 0) == 4 else 1
        else:
            delta = -1 if event.delta > 0 else 1
        self._start_index += delta
        self._clamp_indices()
        self._update_rows()

    def _on_resize(self, event):
        """Handle widget resize and recalculate visible rows.

        Args:
            event: Tkinter configure event.
        """
        if event.widget == self:
            self.after_idle(self._remeasure_and_relayout)

    def _remeasure_and_relayout(self):
        """Measure row height, then recompute sizes and repaint."""
        if not self._rows:
            return

        # Measure actual widget height
        rh = self._rows[0].winfo_height()
        if rh <= 1:
            rh = self._rows[0].winfo_reqheight()

        if rh and rh != self._row_height:
            self._row_height = rh

        # Calculate how many rows fit
        container_height = self._container.winfo_height()
        if container_height > 0:
            visible = max(1, container_height // max(1, self._row_height))
            page_size = visible + OVERSCAN_ROWS

            if visible != self._visible_rows or page_size != self._page_size:
                self._visible_rows = visible
                self._page_size = page_size
                self._ensure_row_pool(self._page_size)

        self._clamp_indices()
        self._update_rows()

    def _on_item_selecting(self, event: Any):
        """Handle item selection event from `ListItem`.

        Args:
            event: Event with `data` for the item being selected.
        """
        record_id = event.data.get('id')
        if record_id is not None and record_id != '__empty__':
            if self._selection_mode == 'single':
                self._datasource.deselect_all()
                self._datasource.select_record(record_id)
            elif self._selection_mode == 'multi':
                if self._datasource.is_selected(record_id):
                    self._datasource.deselect_record(record_id)
                else:
                    self._datasource.select_record(record_id)

            self._update_rows()
            self.event_generate('<<SelectionChange>>')

    def _on_item_removing(self, event: Any):
        """Handle item remove event from `ListItem`.

        Args:
            event: Event with `data` for the item being removed.
        """
        record_id = event.data.get('id')
        if record_id is not None and record_id != '__empty__':
            try:
                self._datasource.delete_record(record_id)
                self._update_rows()
                self.event_generate('<<ItemDelete>>', data=event.data)
            except Exception as exc:
                payload = dict(event.data)
                payload['error'] = str(exc)
                self.event_generate('<<ItemDeleteFail>>', data=payload)

    def _on_item_focused(self, event: Any):
        """Handle item focus event from `ListItem`.

        Args:
            event: Event with `data` for the item being focused.
        """
        record_id = event.data.get('id')
        if record_id is not None and record_id != '__empty__':
            self._focused_record_id = record_id
            self._update_rows()

    def _get_focused_index(self) -> int:
        """Get the data index of the currently focused item.

        Returns:
            The index of the focused item, or -1 if none is focused.
        """
        if self._focused_record_id is None:
            return -1

        # Search visible rows for the focused record
        for i, row in enumerate(self._rows):
            if hasattr(row, '_data') and row._data.get('id') == self._focused_record_id:
                return self._start_index + i

        return -1

    def _focus_item_at_index(self, index: int) -> None:
        """Focus the item at the given data index.

        Args:
            index: The data index of the item to focus.
        """
        total = self._datasource.total_count()
        if total == 0 or index < 0 or index >= total:
            return

        # Scroll if needed to make the item visible
        if index < self._start_index:
            self._start_index = index
            self._clamp_indices()
            self._update_rows()
        elif index >= self._start_index + len(self._rows):
            self._start_index = index - len(self._rows) + 1
            self._clamp_indices()
            self._update_rows()

        # Get the record at the index
        page_data = self._datasource.get_page_from_index(index, 1)
        if page_data:
            record_id = page_data[0].get('id')
            if record_id is not None:
                self._focused_record_id = record_id
                self._update_rows()

                # Focus the visible row widget
                visual_index = index - self._start_index
                if 0 <= visual_index < len(self._rows):
                    self._rows[visual_index].focus_set()

    def _on_arrow_down(self, event) -> str:
        """Handle arrow down key for keyboard navigation.

        Args:
            event: Tkinter key event.

        Returns:
            'break' to prevent default handling.
        """
        total = self._datasource.total_count()
        if total == 0:
            return 'break'

        current_index = self._get_focused_index()
        if current_index < 0:
            # No item focused, focus the first visible item
            next_index = self._start_index
        else:
            # Move to next item
            next_index = min(current_index + 1, total - 1)

        self._focus_item_at_index(next_index)
        return 'break'

    def _on_arrow_up(self, event) -> str:
        """Handle arrow up key for keyboard navigation.

        Args:
            event: Tkinter key event.

        Returns:
            'break' to prevent default handling.
        """
        total = self._datasource.total_count()
        if total == 0:
            return 'break'

        current_index = self._get_focused_index()
        if current_index < 0:
            # No item focused, focus the last visible item
            next_index = min(self._start_index + len(self._rows) - 1, total - 1)
        else:
            # Move to previous item
            next_index = max(current_index - 1, 0)

        self._focus_item_at_index(next_index)
        return 'break'

    def _on_item_click(self, event: Any):
        """Handle item click event from `ListItem`.

        Args:
            event: Event with `data` for the clicked item.
        """
        # Fetch fresh state from datasource to ensure accurate selection/focus state
        record_id = event.data.get('id')
        if record_id is not None and record_id != '__empty__':
            item_index = event.data.get('item_index')
            if item_index is not None:
                page_data = self._datasource.get_page_from_index(item_index, 1)
                if page_data:
                    record = page_data[0].copy()
                    record['selected'] = self._datasource.is_selected(record_id)
                    record['focused'] = (record_id == self._focused_record_id)
                    record['item_index'] = item_index
                    self.event_generate('<<ItemClick>>', data=record)
                    return

        # Fallback to original data if we can't fetch fresh state
        self.event_generate('<<ItemClick>>', data=event.data)

    def _apply_widget_surface(self, row: ListItem, widget_index: int) -> None:
        """Apply surface color to a row widget based on its position in the pool.

        This is called once when a widget is created. The color is based on the
        widget's position (not the data index), creating a stable alternating
        pattern during scrolling without needing to recalculate colors.

        Args:
            row: The ListItem widget to color.
            widget_index: The position of this widget in the row pool (0-based).
        """
        base_surface = getattr(self, "_surface", "background")
        if not self._striped:
            surface = base_surface
        else:
            # Apply striped background to odd rows
            is_odd = (widget_index % 2) == 1
            surface = self._striped_background if is_odd else base_surface

        if hasattr(row, "set_surface"):
            row.set_surface(surface)

    def _on_item_drag_start(self, event: Any):
        """Handle item drag start event from `ListItem`.

        Args:
            event: Event with `data` for the dragged item.
        """
        record_id = event.data.get('id')
        source_index = event.data.get('source_index')
        if record_id is None or record_id == '__empty__' or source_index is None:
            return

        self._drag_state = dict(
            record_id=record_id,
            source_index=source_index,
            target_index=source_index,
            record_data=dict(event.data),
        )
        self._drag_scroll_counter = 0
        self._show_drag_indicator()
        self._update_drag_indicator_position(source_index)
        self.event_generate('<<ItemDragStart>>', data=event.data)

    def _on_item_dragging(self, event: Any):
        """Handle item dragging event from `ListItem`.

        Args:
            event: Event with `data` for the dragged item.
        """
        if not self._drag_state:
            return

        y_current = event.data.get('y_current')
        target_index = self._get_drop_index(y_current)
        self._drag_state['target_index'] = target_index
        self._auto_scroll_for_drag(y_current)
        self._update_drag_indicator_position(target_index)
        payload = dict(self._drag_state.get('record_data', {}))
        payload.update(
            dict(
                source_index=self._drag_state.get('source_index'),
                target_index=target_index,
                y_current=y_current,
            )
        )
        self.event_generate('<<ItemDrag>>', data=payload)

    def _on_item_drag_end(self, event: Any):
        """Handle item drag end event from `ListItem`.

        Args:
            event: Event with `data` for the dragged item.
        """
        if not self._drag_state:
            return

        self._hide_drag_indicator()

        record_id = self._drag_state.get('record_id')
        target_index = self._drag_state.get('target_index')
        moved = self._move_record(record_id, target_index)
        if moved:
            self._update_rows()

        payload = dict(self._drag_state.get('record_data', {}))
        payload.update(
            dict(
                source_index=self._drag_state.get('source_index'),
                target_index=target_index,
                y_end=event.data.get('y_end'),
                y_start=event.data.get('y_start'),
            )
        )
        payload['target_index'] = target_index
        payload['moved'] = moved
        self.event_generate('<<ItemDragEnd>>', data=payload)
        self._drag_state = None

    def _get_drop_index(self, y_root: int | None) -> int:
        """Calculate the drop index for a drag operation.

        Args:
            y_root: Screen Y coordinate.

        Returns:
            Zero-based index for the drop position.
        """
        total = self._datasource.total_count()
        if total <= 0:
            return 0

        if y_root is None:
            return max(0, min(self._start_index, total - 1))

        container_top = self._container.winfo_rooty()
        container_height = self._container.winfo_height()
        if container_height <= 0:
            return max(0, min(self._start_index, total - 1))

        y_local = y_root - container_top
        y_local = max(0, min(y_local, container_height - 1))
        offset = int(y_local // max(1, self._row_height))
        target = self._start_index + offset
        return max(0, min(target, total - 1))

    def _auto_scroll_for_drag(self, y_root: int | None) -> None:
        """Auto-scroll while dragging near the list edges.

        Args:
            y_root: Screen Y coordinate.
        """
        if y_root is None:
            return

        container_top = self._container.winfo_rooty()
        container_height = self._container.winfo_height()
        if container_height <= 0:
            return

        scroll_zone_height = max(10, int(container_height * 0.2))
        container_bottom = container_top + container_height
        self._drag_scroll_counter += 1
        should_scroll = self._drag_scroll_counter % 8 == 0
        if should_scroll:
            if y_root < container_top + scroll_zone_height:
                self._start_index -= 1
            elif y_root > container_bottom - scroll_zone_height:
                self._start_index += 1
            else:
                return
        else:
            return

        self._clamp_indices()
        self._update_rows()

    def _move_record(self, record_id: Any, target_index: int | None) -> bool:
        """Move a record in the data source if supported.

        Args:
            record_id: Record identifier to move.
            target_index: Target index to move the record to.

        Returns:
            True if the record was moved.
        """
        if record_id is None or target_index is None:
            return False

        mover = getattr(self._datasource, 'move_record', None)
        if callable(mover):
            return bool(mover(record_id, target_index))

        # Fallback for simple in-memory lists
        try:
            total = self._datasource.total_count()
            all_records = self._datasource.get_page_from_index(0, total)
            source_index = None
            for i, record in enumerate(all_records):
                if record.get('id') == record_id:
                    source_index = i
                    break
            if source_index is None:
                return False
            clamped_target = max(0, min(target_index, len(all_records) - 1))
            if source_index == clamped_target:
                return False
            record = all_records.pop(source_index)
            if clamped_target > source_index:
                clamped_target -= 1
            all_records.insert(clamped_target, record)
            setter = getattr(self._datasource, 'set_data', None)
            if callable(setter):
                setter(all_records)
                return True
        except Exception:
            return False

        return False

    def _show_drag_indicator(self) -> None:
        """Create and show the drag drop indicator line."""
        if self._drag_indicator is None:
            self._drag_indicator = Frame(self._container, accent=self._accent)

    def _update_drag_indicator_position(self, target_index: int) -> None:
        """Update the drag indicator to show drop location."""
        if self._drag_indicator is None:
            return

        try:
            visual_index = target_index - self._start_index
            if 0 <= visual_index < len(self._rows):
                y_pos = visual_index * max(1, self._row_height)
                self._drag_indicator.place(
                    x=0,
                    y=y_pos,
                    width=self._container.winfo_width(),
                    height=3,
                )
                self._drag_indicator.lift()
            else:
                self._drag_indicator.place_forget()
        except Exception:
            pass

    def _hide_drag_indicator(self) -> None:
        """Hide and destroy the drag indicator."""
        if self._drag_indicator is not None:
            try:
                self._drag_indicator.place_forget()
                self._drag_indicator.destroy()
            except Exception:
                pass
            self._drag_indicator = None

    # Public API

    def reload(self):
        """Reload data from the datasource and refresh the display.

        Calls the datasource's `reload()` method and updates all visible rows
        with the refreshed data. Useful when the underlying data has changed
        externally.
        """
        self._datasource.reload()
        self._update_rows()

    def get_selected(self) -> list[dict]:
        """Get the currently selected records.

        Returns:
            List of selected record dictionaries (each with `id` and the
            record's data). Empty list if no items are selected.

        Examples:
            >>> selected = listview.get_selected()
            >>> for record in selected:
            ...     print(record["id"], record.get("title"))
        """
        return self._datasource.get_selected()

    def select_all(self):
        """Select all items in the list.

        Only works when selection_mode is 'multi'. Generates a
        <<SelectionChange>> event after completion.

        Note:
            For large datasets, this may be slow as it loads all records.
        """
        if self._selection_mode == 'multi':
            total = self._datasource.total_count()
            all_records = self._datasource.get_page_from_index(0, total)
            for record in all_records:
                record_id = record.get('id')
                if record_id:
                    self._datasource.select_record(record_id)
            self._update_rows()
            self.event_generate('<<SelectionChange>>')

    def clear_selection(self):
        """Clear all item selections.

        Deselects all items and generates a <<SelectionChange>> event.
        """
        self._datasource.deselect_all()
        self._update_rows()
        self.event_generate('<<SelectionChange>>')

    def scroll_to_top(self):
        """Scroll to the beginning of the list.

        Instantly scrolls to show the first item in the list.
        """
        self._start_index = 0
        self._update_rows()

    def scroll_to_bottom(self):
        """Scroll to the end of the list.

        Instantly scrolls to show the last items in the list.
        """
        total = self._datasource.total_count()
        self._start_index = max(0, total - self._visible_rows)
        self._update_rows()

    def insert_item(self, data: dict):
        """Insert a new item into the list.

        Args:
            data: Dictionary containing the item data. An 'id' will be
                auto-generated if not provided.

        Note:
            Generates a <<ItemInsert>> event after the item is added.
            `event.data` is the inserted record dict with `id` populated.

        Examples:
            >>> listview.insert_item({
            ...     'title': 'New Item',
            ...     'text': 'Description'
            ... })
        """
        record_id = self._datasource.create_record(data)
        self._update_rows()
        record = dict(data)
        record.setdefault('id', record_id)
        self.event_generate('<<ItemInsert>>', data=record)

    def update_item(self, record_id: Any, data: dict):
        """Update an existing item's data.

        Args:
            record_id: The ID of the record to update.
            data: Dictionary of fields to update. Will be merged with
                existing record data.

        Note:
            Generates a <<ItemUpdate>> event if the update succeeds.
            `event.data` is the patch dict with `id` set to `record_id`.

        Examples:
            >>> listview.update_item(42, {'title': 'Updated Title'})
        """
        if self._datasource.update_record(record_id, data):
            self._update_rows()
            record = dict(data)
            record['id'] = record_id
            self.event_generate('<<ItemUpdate>>', data=record)

    def delete_item(self, record_id: Any):
        """Delete an item from the list.

        Args:
            record_id: The ID of the record to delete.

        Note:
            Generates a <<ItemDelete>> event after deletion.
            `event.data = {'id': record_id}`.

        Examples:
            >>> listview.delete_item(42)
        """
        self._datasource.delete_record(record_id)
        self._update_rows()
        self.event_generate('<<ItemDelete>>', data={'id': record_id})

    def get_datasource(self) -> DataSourceProtocol:
        """Get the underlying datasource.

        Returns:
            The DataSource instance managing the list's data.

        Examples:
            >>> ds = listview.get_datasource()
            >>> count = ds.total_count()
        """
        return self._datasource

    # Event handler API

    def on_selection_changed(self, callback: Callable) -> str:
        """Bind to `<<SelectionChange>>`. Callback receives `event.data = None` (use `get_selected()` to get current selection)."""
        return self.bind('<<SelectionChange>>', callback, add='+')

    def off_selection_changed(self, bind_id: str | None = None) -> None:
        """Unbind from `<<SelectionChange>>`."""
        self.unbind('<<SelectionChange>>', bind_id)

    def on_item_delete(self, callback: Callable) -> str:
        """Bind to `<<ItemDelete>>`. Callback receives `event.data = dict` (the deleted record, with at least `id`)."""
        return self.bind('<<ItemDelete>>', callback, add='+')

    def off_item_delete(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemDelete>>`."""
        self.unbind('<<ItemDelete>>', bind_id)

    def on_item_delete_fail(self, callback: Callable) -> str:
        """Bind to `<<ItemDeleteFail>>`. Callback receives `event.data = dict` (the record plus an `error: str` key)."""
        return self.bind('<<ItemDeleteFail>>', callback, add='+')

    def off_item_delete_fail(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemDeleteFail>>`."""
        self.unbind('<<ItemDeleteFail>>', bind_id)

    def on_item_insert(self, callback: Callable) -> str:
        """Bind to `<<ItemInsert>>`. Callback receives `event.data = dict` (the inserted record, with `id` populated)."""
        return self.bind('<<ItemInsert>>', callback, add='+')

    def off_item_insert(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemInsert>>`."""
        self.unbind('<<ItemInsert>>', bind_id)

    def on_item_update(self, callback: Callable) -> str:
        """Bind to `<<ItemUpdate>>`. Callback receives `event.data = dict` (the patch dict with `id` set)."""
        return self.bind('<<ItemUpdate>>', callback, add='+')

    def off_item_update(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemUpdate>>`."""
        self.unbind('<<ItemUpdate>>', bind_id)

    def on_item_click(self, callback: Callable) -> str:
        """Bind to `<<ItemClick>>`. Callback receives `event.data = dict` (the record, with `selected`, `focused`, `item_index` injected)."""
        return self.bind('<<ItemClick>>', callback, add='+')

    def off_item_click(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemClick>>`."""
        self.unbind('<<ItemClick>>', bind_id)

    def on_item_drag_start(self, callback: Callable) -> str:
        """Bind to `<<ItemDragStart>>`. Callback receives `event.data = dict` (the record)."""
        return self.bind('<<ItemDragStart>>', callback, add='+')

    def off_item_drag_start(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemDragStart>>`."""
        self.unbind('<<ItemDragStart>>', bind_id)

    def on_item_drag(self, callback: Callable) -> str:
        """Bind to `<<ItemDrag>>`. Callback receives `event.data = dict` (record plus `source_index`, `target_index`, `y_current`)."""
        return self.bind('<<ItemDrag>>', callback, add='+')

    def off_item_drag(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemDrag>>`."""
        self.unbind('<<ItemDrag>>', bind_id)

    def on_item_drag_end(self, callback: Callable) -> str:
        """Bind to `<<ItemDragEnd>>`. Callback receives `event.data = dict` (record plus `source_index`, `target_index`, `moved`, `y_start`, `y_end`)."""
        return self.bind('<<ItemDragEnd>>', callback, add='+')

    def off_item_drag_end(self, bind_id: str | None = None) -> None:
        """Unbind from `<<ItemDragEnd>>`."""
        self.unbind('<<ItemDragEnd>>', bind_id)
