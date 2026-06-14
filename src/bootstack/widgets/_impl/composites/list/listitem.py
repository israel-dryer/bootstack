from tkinter import TclError
from typing import Literal

from typing_extensions import Unpack

from bootstack.widgets._impl.composites.compositeframe import CompositeFrame
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets.types import Master, StyledKwargs, WidgetDensity
from bootstack.style.typography import get_font


class ListItemKwargs(StyledKwargs, total=False):
    """Kwargs for ListItem."""
    show_separator: bool
    show_chevron: bool
    focusable: bool
    hoverable: bool
    draggable: bool
    removable: bool
    selection_mode: Literal['none', 'single', 'multi']
    show_selection_controls: bool
    select_on_click: bool
    density: WidgetDensity


class ListItem(CompositeFrame):
    """A list item widget with support for icons, text, badges, and interactive controls.

    ListItem extends CompositeFrame to provide automatic state synchronization
    across all child widgets. It supports selection modes, focus states, dragging,
    removal, and various visual customizations.

    The widget automatically handles hover, pressed, and focus states across all
    registered child widgets using the Composite state coordinator.

    Data fields:
        When update_data() is called, the following fields are recognized:
        - id: Unique identifier for the item (required for selection/removal).
        - title: Primary text displayed in bold body font.
        - text: Secondary text displayed below the title.
        - icon: Icon name or configuration to display on the left.
        - badge: Short label displayed on the right.
        - selected: Boolean indicating if the item is selected.
        - focused: Boolean indicating if the item has keyboard focus.
        - item_index: Zero-based index of the item in the list.
    """

    def __init__(self, master: Master = None, **kwargs: Unpack[ListItemKwargs]) -> None:
        """Initialize a ListItem widget.

        Args:
            master: Parent widget.
            show_separator: Show separator line below the item. Default False.
            show_chevron: Show chevron indicator on the right. Default False.
            focusable: Whether this item can receive keyboard focus. Default True.
            hoverable: Whether this item shows hover state. Default False.
            draggable: Whether this item can be dragged. Default False.
            removable: Whether this item can be removed. Default False.
            selection_mode: Selection mode ('none', 'single', 'multi'). Default 'none'.
            show_selection_controls: Show checkbox/radio button. Default False.
            select_on_click: Whether clicking selects the item. Defaults to True when
                selection_mode is 'single' or 'multi', False otherwise.
            density: Visual density ('default' or 'compact'). Default 'default'.
            **kwargs: Additional arguments forwarded to CompositeFrame.
        """
        # state tracking
        self._data = {}
        self._state = {}
        self._item_index = 0
        self._selection_icon = None
        self._drag_state = None
        # Full (untruncated) title/text — the labels render an ellipsized copy
        # sized to the row's available width (see _retruncate).
        self._full_title = None
        self._full_text = None
        self._last_avail = -1

        # configuration properties
        self._show_separator = kwargs.pop('show_separator', False)
        self._show_chevron = kwargs.pop('show_chevron', False)
        self._focusable = kwargs.pop('focusable', True)
        self._hoverable = kwargs.pop('hoverable', False)
        self._draggable = kwargs.pop('draggable', False)
        self._removable = kwargs.pop('removable', False)
        # Capture accent (pop) so super() doesn't get it twice, and we can pass it
        # explicitly to super() below.
        self._accent = kwargs.pop('accent', None) or 'primary'
        self._selection_mode = kwargs.pop('selection_mode', 'none')
        self._show_selection_controls = kwargs.pop('show_selection_controls', False)
        self._density = kwargs.pop('density', 'default')
        # Divider color for a separated row (set to the stripe color when striped
        # so the divider matches the band instead of a darker line).
        self._separator_color = kwargs.pop('separator_color', None)

        # Determine if clicking should trigger selection
        # If selection mode is active (single/multi), enable click selection
        # If selection mode is 'none', respect the select_on_click parameter
        select_on_click = kwargs.pop('select_on_click', self._selection_mode != 'none')
        self._select_on_click = select_on_click

        self._get_selection_icon()

        # Selected rows always show the wash, even alongside a selection control:
        # wash + control, consistent with DataTable.
        self._wash = True

        # Adjust padding based on density
        item_padding = (6, 3) if self._density == 'compact' else (8, 4)

        # Initialize CompositeFrame with selection disabled (we handle it ourselves)
        super().__init__(
            master=master,
            select_on_click=False,
            variant='separated_item' if self._show_separator else 'item',
            takefocus=self._focusable,
            ttk_class='ListView.TFrame',
            padding=item_padding,
            accent=self._accent,
            style_options=self._li_style_opts(),
        )

        # composite container widgets
        self._left_frame = Frame(
            self,
            variant='list',
            ttk_class='ListView.TFrame',
            takefocus=False,
            accent=self._accent,
            style_options=self._li_style_opts()
        )
        self._left_frame.pack(side='left')

        self._center_frame = Frame(
            self,
            variant='list',
            ttk_class='ListView.TFrame',
            takefocus=False,
            accent=self._accent,
            style_options=self._li_style_opts()
        )
        self._center_frame.pack(side='left', fill='x', expand=True)

        self._right_frame = Frame(
            self,
            variant='list',
            ttk_class='ListView.TFrame',
            takefocus=False,
            accent=self._accent,
            style_options=self._li_style_opts()
        )
        self._right_frame.pack(side='left')

        # conditional widgets
        self._separator = Separator(self)
        self._selection_widget = None
        self._icon_widget = None
        self._title_widget = None
        self._text_widget = None
        self._caption_widget = None
        self._remove_widget = None
        self._badge_widget = None
        self._chevron_widget = None
        self._drag_widget = None

        # Register container frames with composite coordinator
        for widget in [self._left_frame, self._center_frame, self._right_frame]:
            self.register_composite(widget)

        # Bind to composite invoke for selection and/or focus handling
        if self._select_on_click or self._focusable:
            self.on_invoked(self._on_click)

        # Focus event handling (notify ListView of focus changes)
        if self._focusable:
            self.bind('<FocusIn>', self._on_focus_in, add='+')
            self.bind('<FocusOut>', self._on_focus_out, add='+')

        # row-level keyboard events
        self.bind('<space>', self._on_space, add='+')

        # Re-ellipsize the title/text whenever the center frame's allotment
        # changes (sidebar resize, or the icon/chevron settling) so a long value
        # can never push the icon/chevron out of the row.
        self._center_frame.bind('<Configure>', self._on_configure_truncate, add='+')

    @property
    def selected(self):
        """bool: Current selection state from data."""
        return self._data.get('selected')

    @property
    def data(self):
        """dict: The data record associated with this list item."""
        return self._data

    def _li_style_opts(self) -> dict:
        """Common style options for child widgets (carries the wash flag)."""
        opts = dict(hoverable=self._hoverable, density=self._density, wash=self._wash)
        if self._separator_color:
            opts['separator'] = self._separator_color
        return opts

    def _get_selection_icon(self):
        """Determine the selection icon based on selection mode."""
        if self._selection_mode == 'multi':
            self._selection_icon = dict(name='square', state=[('selected', "check-square-fill")])
        elif self._selection_mode == 'single':
            self._selection_icon = dict(name='circle', state=[('selected', "check-circle-fill")])
        else:
            self._selection_icon = None

    def _on_click(self, event):
        """Handle click on the list item."""
        if self._focusable:
            self.focus()
        # notify parent list that item has been clicked
        self.master.event_generate('<<ItemClick>>', data=self._data)
        self.select()

    def _on_space(self, event):
        """Handle space key press."""
        if self._focusable:
            self.focus()
        # notify parent list that item has been clicked
        self.master.event_generate('<<ItemClick>>', data=self._data)
        self.select()

    def _on_focus_in(self, event):
        """Handle focus in event - notify ListView."""
        self._data['focused'] = True
        self.master.event_generate('<<ItemFocus>>', data=self._data)

    def _on_focus_out(self, event):
        """Handle focus out event - check if focus moved to descendant."""
        # Keep focus styling if focus moved to a descendant of this row
        related = getattr(event, 'related', None)
        try:
            if related is not None and str(related).startswith(str(self)):
                return 'break'
        except TclError:
            pass

        self._data['focused'] = False

    def _update_selection(self, selected: bool = False):
        """Apply selection state atomically (style + icon) with null guards."""
        mode = self._selection_mode

        if mode == 'none':
            if self._selection_widget is not None:
                try:
                    self._selection_widget.pack_forget()
                except TclError:
                    pass
                try:
                    self._selection_widget.destroy()
                except TclError:
                    pass

            self._selection_widget = None
            # Use CompositeFrame's set_selected to clear selection
            self.set_selected(False)

            # Notify widgets
            for w in self._composite._composites:
                try:
                    w.event_generate('<<CompositeDeselect>>')
                except TclError:
                    pass

            # keep a remembered icon so later comparisons are cheap
            if hasattr(self, '_state'):
                self._state['__sel_icon'] = None
                self._state['selected'] = False
            return

        # ensure state cache exists
        if not hasattr(self, '_state'):
            self._state = {}

        # ensure the selection control exists even if not visible
        if self._selection_widget is None:
            self._selection_widget = Label(
                self._left_frame,
                icon=self._selection_icon,
                variant='selection',
                ttk_class='ListView.TLabel',
                icon_only=True,
                accent=self._accent,
                style_options=self._li_style_opts(),
                takefocus=False,
            )
            if self._show_selection_controls:
                self._selection_widget.pack(side='left', padx=5)
            self.register_composite(self._selection_widget)

        # Use CompositeFrame's set_selected to apply state
        self.set_selected(selected)

        # Notify widgets
        for w in self._composite._composites:
            try:
                w.event_generate('<<CompositeSelect>>' if selected else '<<CompositeDeselect>>')
            except TclError:
                pass

        # remember logical selected flag
        self._state['selected'] = bool(selected)

    def _update_icon(self, icon=None):
        """Update icon widget, or create if not existing."""
        if icon is not None:
            if not self._icon_widget:
                self._icon_widget = Label(
                    self._left_frame,
                    icon=icon,
                    variant='icon',
                    ttk_class='ListView.TLabel',
                    takefocus=False,
                    icon_only=True,
                    accent=self._accent,
                    style_options=self._li_style_opts(),
                )
                self._icon_widget.pack(side='left', padx=5)
                self.register_composite(self._icon_widget)
            else:
                self._icon_widget.configure(icon=icon)
        else:
            if self._icon_widget:
                try:
                    self._icon_widget.pack_forget()
                    self._icon_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._icon_widget = None

    def _update_title(self, text=None):
        """Update title widget."""
        title_font = 'caption[bold]' if self._density == 'compact' else 'body[bold]'
        self._full_title = text
        if text is not None:
            shown = self._elide(text, get_font(title_font), self._avail_text_px())
            if not self._title_widget:
                self._title_widget = Label(
                    self._center_frame,
                    text=shown,
                    font=title_font,
                    variant='list',
                    ttk_class='ListView.TLabel',
                    takefocus=False,
                    accent=self._accent,
                    # width=1 so the label never drives the center frame wider
                    # than its allotment — fill='x' stretches it back out, and
                    # the elided text is sized to that allotment (see _retruncate).
                    width=1,
                    style_options=self._li_style_opts(),
                )
                self._title_widget.pack(side='top', fill='x', anchor='w', padx=(0, 3))
                self.register_composite(self._title_widget)
            else:
                self._title_widget.configure(text=shown)
        else:
            if self._title_widget:
                try:
                    self._title_widget.pack_forget()
                    self._title_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._title_widget = None

    def _update_text(self, text=None):
        """Update text widget."""
        # Use caption font for compact density
        text_font = 'caption' if self._density == 'compact' else 'body'
        self._full_text = text
        if text is not None:
            shown = self._elide(text, get_font(text_font), self._avail_text_px())
            if not self._text_widget:
                self._text_widget = Label(
                    self._center_frame,
                    text=shown,
                    font=text_font,
                    variant='list',
                    ttk_class='ListView.TLabel',
                    takefocus=False,
                    accent=self._accent,
                    width=1,
                    style_options=self._li_style_opts(),
                )
                self._text_widget.pack(side='top', fill='x', padx=(0, 3))
                self.register_composite(self._text_widget)
            else:
                self._text_widget.configure(text=shown)
        else:
            if self._text_widget:
                try:
                    self._text_widget.pack_forget()
                    self._text_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._text_widget = None

    # ----- Title/text ellipsis -----

    def _avail_text_px(self) -> int:
        """Pixels available to the center title/text before they must elide.

        Read straight off the center frame's own allotted width. Because the
        labels carry `width=1`, the center frame never inflates past its
        allotment, so this is the true available width and it re-fires its
        `<Configure>` whenever the icon/chevron settle or the sidebar resizes.
        """
        try:
            w = self._center_frame.winfo_width()
            if w <= 1:
                return 0
            # 3px = the label's own right padx.
            return max(0, w - 3)
        except TclError:
            return 0

    @staticmethod
    def _elide(text, font, avail: int):
        """Return `text` shortened with a trailing ellipsis to fit `avail` px."""
        if not text or avail <= 0:
            return text
        try:
            if font.measure(text) <= avail:
                return text
            ell = '…'
            if font.measure(ell) > avail:
                return ''
            lo, hi = 0, len(text)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if font.measure(text[:mid].rstrip() + ell) <= avail:
                    lo = mid
                else:
                    hi = mid - 1
            return (text[:lo].rstrip() + ell) if lo > 0 else ell
        except TclError:
            return text

    def _on_configure_truncate(self, event=None):
        """Re-ellipsize when the row's available width changes."""
        avail = self._avail_text_px()
        if avail <= 0 or avail == self._last_avail:
            return
        self._last_avail = avail
        self._retruncate(avail)

    def _retruncate(self, avail: int | None = None):
        """Re-apply ellipsis to the title/text against the current width."""
        if avail is None:
            avail = self._avail_text_px()
        if avail <= 0:
            return
        if self._title_widget and self._full_title is not None:
            font = get_font('caption[bold]' if self._density == 'compact' else 'body[bold]')
            self._title_widget.configure(text=self._elide(self._full_title, font, avail))
        if self._text_widget and self._full_text is not None:
            font = get_font('caption' if self._density == 'compact' else 'body')
            self._text_widget.configure(text=self._elide(self._full_text, font, avail))

    def _update_badge(self, text=None):
        """Update badge widget."""
        if text is not None:
            if not self._badge_widget:
                self._badge_widget = Label(
                    self._right_frame,
                    text=text,
                    variant='list',
                    ttk_class='ListView.TLabel',
                    accent=self._accent,
                    style_options=self._li_style_opts(),
                )
                self._badge_widget.pack(side='right', padx=6)
                self.register_composite(self._badge_widget)
            else:
                self._badge_widget.configure(text=text)
        else:
            if self._badge_widget:
                try:
                    self._badge_widget.pack_forget()
                    self._badge_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._badge_widget = None

    def _update_chevron(self):
        """Update or create chevron widget."""
        if self._show_chevron:
            if not self._chevron_widget:
                self._chevron_widget = Button(
                    self._right_frame,
                    icon='chevron-right',
                    icon_only=True,
                    variant='icon',
                    ttk_class='ListView.TButton',
                    takefocus=False,
                    accent=self._accent,
                    style_options=self._li_style_opts(),
                )
                self._chevron_widget.pack(side='right', padx=6)
                self.register_composite(self._chevron_widget)
                # The chevron is created lazily (after_idle), after the row's
                # selection state was already applied to the other composites —
                # so it misses the sync. Its selected color comes from the ttk
                # 'selected' STATE (see CompositeFrame._update_states), not the
                # <<CompositeSelect>> event, so apply that state directly now;
                # otherwise a row selected on first load shows an unselected
                # chevron color.
                if self._data.get('selected'):
                    try:
                        self._chevron_widget.state(['selected'])
                    except TclError:
                        pass
        else:
            if self._chevron_widget:
                try:
                    self._chevron_widget.pack_forget()
                    self._chevron_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._chevron_widget = None

    def _update_remove(self):
        """Update or create remove button widget."""
        if self._removable:
            if not self._remove_widget:
                self._remove_widget = Button(
                    self._right_frame,
                    icon='x-lg',
                    icon_only=True,
                    variant='icon',
                    ttk_class='ListView.TButton',
                    takefocus=False,
                    command=self.remove,
                    accent=self._accent,
                    style_options=self._li_style_opts(),
                )
                self._remove_widget.pack(side='right', padx=6)
                self.register_composite(self._remove_widget)
        else:
            if self._remove_widget:
                try:
                    self._remove_widget.pack_forget()
                    self._remove_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._remove_widget = None

    def _update_drag(self):
        """Update or create drag handle widget."""
        if self._draggable:
            if not self._drag_widget:
                self._drag_widget = Button(
                    self._right_frame,
                    icon='grip-vertical',
                    icon_only=True,
                    variant='icon',
                    ttk_class='ListView.TButton',
                    cursor='fleur',
                    takefocus=False,
                    accent=self._accent,
                    style_options=self._li_style_opts(),
                )
                self._drag_widget.pack(side='right', padx=6)

                # Setup drag detection
                self._drag_state = {'dragging': False, 'start_y': None}
                self._drag_widget.bind('<ButtonPress-1>', self._on_drag_mouse_down, add='+')
                self._drag_widget.bind('<B1-Motion>', self._on_drag_mouse_motion, add='+')
                self._drag_widget.bind('<ButtonRelease-1>', self._on_drag_mouse_up, add='+')
                self.register_composite(self._drag_widget)
        else:
            if self._drag_widget:
                try:
                    self._drag_widget.pack_forget()
                    self._drag_widget.destroy()
                except TclError:
                    pass
                finally:
                    self._drag_widget = None
                    self._drag_state = None

    def set_surface(self, surface: str) -> None:
        """Set the surface color for the row and its container frames.

        This method is used by ListView to apply alternating row colors efficiently.
        The surface color is set once when the widget is created and remains stable
        during scrolling.

        Args:
            surface: Surface color name or value (e.g., 'background', 'background[+1]').
        """
        previous = getattr(self, "_surface", "background")
        self.configure_style_options(surface=surface)
        if previous != surface:
            self.rebuild_style()

        for frame in (self._left_frame, self._center_frame, self._right_frame):
            try:
                frame.configure_style_options(surface=surface)
                frame.rebuild_style()
            except Exception:
                continue

    # ---- Event Handlers (Drag-related) ----

    def _on_drag_mouse_down(self, event):
        """Mouse pressed on drag handle - prepare for drag."""
        if not hasattr(self, '_drag_state'):
            self._drag_state = {}
        self._drag_state['start_y'] = event.y_root
        self._drag_state['dragging'] = False

    def _on_drag_mouse_motion(self, event):
        """Mouse moving with button held - this is a drag."""
        if not hasattr(self, '_drag_state') or self._drag_state.get('start_y') is None:
            return

        # if this is the first motion event, emit drag start
        if not self._drag_state.get('dragging'):
            self._drag_state['dragging'] = True
            self.master.event_generate(
                '<<ItemDragStart>>',
                data={**self._data, 'source_index': self._item_index, 'y_start': self._drag_state['start_y']}
            )

        # emit drag motion event
        self.master.event_generate(
            '<<ItemDrag>>',
            data={
                **self._data,
                'source_index': self._item_index,
                'y_current': event.y_root,
                'y_start': self._drag_state['start_y'],
                'delta_y': event.y_root - self._drag_state['start_y']
            }
        )

    def _on_drag_mouse_up(self, event):
        """Mouse release - end drag if we were dragging."""
        if not hasattr(self, '_drag_state'):
            return

        # only emit drag end if we actually started dragging
        if self._drag_state.get('dragging'):
            self.master.event_generate('<<ItemDragEnd>>',
                                       data={
                                           **self._data,
                                           'source_index': self._item_index,
                                           'y_end': event.y_root,
                                           'y_start': self._drag_state.get('start_y')
                                       })
        # reset drag state
        self._drag_state = {'dragging': False, 'start_y': None}

    # --- Configuration delegates ---

    @configure_delegate('selection_mode')
    def _delegate_selection_mode(self, value=None):
        self._selection_mode = value
        self._get_selection_icon()

    @configure_delegate('show_selection_controls')
    def _delegate_show_selection_controls(self, value=None):
        self._show_selection_controls = value
        self._get_selection_icon()
        self._update_selection(False)

    @configure_delegate('show_chevron')
    def _delegate_show_chevron(self, value=None):
        self._show_chevron = value
        self._update_chevron()

    @configure_delegate('draggable')
    def _delegate_draggable(self, value=None):
        self._draggable = value
        self._update_drag()

    @configure_delegate('removable')
    def _delegate_removable(self, value=None):
        self._removable = value
        self._update_remove()

    # ---- Public API ----

    def select(self):
        """Toggle or set the selection state based on selection mode.

        Returns:
            bool or None: True if selected, False if deselected, None if no action.
        """
        mode = self._selection_mode
        if mode == 'none':
            return None

        is_selected = bool(self.selected or False)
        if is_selected:
            if mode == 'single':
                return None
            self._data['selected'] = False
            self.master.event_generate('<<ItemSelecting>>', data=self._data)
            return False

        self._data['selected'] = True
        self.master.event_generate('<<ItemSelecting>>', data=self._data)
        return True

    def remove(self):
        """Notify subscribers to handle remove action."""
        self.master.event_generate('<<ItemRemoving>>', data=self._data)

    def update_data(self, record: dict | None):
        """Update row visuals efficiently when values have changed.

        Args:
            record: Dictionary containing the item data. If None or contains
                '__empty__' key, the item will be hidden.
        """
        if record is None or '__empty__' in record:
            self.pack_forget()
            return

        if not self.winfo_manager():
            self.pack(fill='x')

        self._data = record
        self._item_index = self._data.get('item_index', 0)

        selected = bool(record.get('selected', False))

        # handle focus - apply tkinter focus to the widget that should have logical focus
        focused = bool(record.get('focused', False))
        if self._state.get('focused') != focused and self._focusable:
            if focused:
                # this record should have focus - give tkinter focus to this widget
                try:
                    self.focus_set()
                    self._data['focused'] = True
                except TclError:
                    pass
            else:
                # This record lost focus - clear tkinter focus if we have it,
                # and drop the keyboard-focus ring state so a recycled/relocated
                # row doesn't keep a stale ring.
                try:
                    if self.focus_get() == self:
                        # Move focus to parent container
                        self.master.focus_set()
                except (TclError, AttributeError):
                    pass
                try:
                    self.state(['!background'])
                except TclError:
                    pass
                self._data['focused'] = False
            self._state['focused'] = focused

        # Create/update field widgets first so they exist before selection state is applied
        for field, updater in {
            "title": self._update_title,
            "text": self._update_text,
            "icon": self._update_icon,
        }.items():
            value = record.get(field)
            if self._state.get(field) != value:
                updater(value)
                self._state[field] = value

        # Apply selection after widgets exist so _update_states reaches all composites
        if self._state.get('selected') != selected:
            self._update_selection(selected)
            self._state['selected'] = selected

        def _safe(fn):
            def _call():
                try:
                    if self.winfo_exists():
                        fn()
                except TclError:
                    pass
            return _call

        self.after_idle(_safe(self._update_chevron))
        self.after_idle(_safe(self._update_drag))
        self.after_idle(_safe(self._update_remove))