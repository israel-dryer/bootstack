"""Date entry field widget with calendar picker button.

Provides a specialized entry field for date input with locale-aware formatting
and an optional calendar picker button.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Iterable, Literal
from bootstack.i18n.intl_format import DateFormatSpec

from typing_extensions import Unpack

from bootstack.events import ChangeEvent
from bootstack.widgets._impl.primitives.button import Button
from bootstack.widgets._impl.composites.field import Field, FieldOptions
from bootstack.widgets._impl.mixins import configure_delegate
from bootstack.widgets.types import Master

if TYPE_CHECKING:
    pass


class DateEntry(Field):
    """A date entry field widget with calendar picker button.

    DateEntry extends the Field widget to provide specialized date input with
    locale-aware formatting and an optional calendar picker button. The widget
    supports various date format presets and custom ICU date format patterns,
    and can accept input as strings, date objects, or datetime objects.

    The available date format presets are: `longDate` (January 15, 2025),
    `shortDate` (1/15/25), `monthAndDate` (January 15), `monthAndYear`
    (January 2025), `quarterAndYear` (Q1 2025), `day` (15), `dayOfWeek`
    (Wednesday), `month` (January), `quarter` (Q1), `year` (2025),
    `longTime` (3:30:45 PM PST), `shortTime` (3:30 PM), `longDateLongTime`,
    `shortDateShortTime`, or any custom ICU date format pattern (e.g., "yyyy-MM-dd").
    """

    def __init__(
            self,
            master: Master = None,
            value: str | date | datetime = None,
            value_format: DateFormatSpec = "longDate",
            label: str = None,
            message: str = None,
            show_picker_button=True,
            picker_title: str = None,
            picker_first_weekday: int = 6,
            selection_mode: Literal["single", "range"] = "single",
            start_date: date | datetime | str | None = None,
            end_date: date | datetime | str | None = None,
            min_date: date | datetime | str | None = None,
            max_date: date | datetime | str | None = None,
            disabled_dates: Iterable[date | datetime | str] | None = None,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial date value to display (single
                mode). Ignored when `selection_mode='range'`.
            value_format: Date format pattern to use for parsing and displaying
                dates. See class docstring for complete list of presets.
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended.
            message: Optional message text to display below the entry field.
                Used for hints or help text. Replaced by validation errors when
                validation fails.
            show_picker_button: If True, displays the calendar picker button
                to the right of the entry. If False, hides the button.
            picker_title: Title text for the calendar picker dialog. Defaults
                to "Select date range" in range mode and "Select new date" otherwise.
            picker_first_weekday: First day of the week to display in the
                calendar picker. 0=Monday, 6=Sunday.
            selection_mode: `'single'` (default) for a single date or
                `'range'` for a start/end date range. In range mode the entry
                is readonly and the user selects dates exclusively via the picker.
                `value` returns `tuple[date, date] | None` in range mode.
            start_date: Initial range start date (range
                mode only).
            end_date: Initial range end date (range mode
                only).
            min_date: Lower bound for selectable dates.
                Dates before this are disabled in the picker.
            max_date: Upper bound for selectable dates.
                Dates after this are disabled in the picker.
            disabled_dates: Specific dates to disable in the picker.

        Other Parameters:
            locale: Locale identifier for date formatting (e.g., 'en_US').
            required: If True, field cannot be empty.
            allow_blank: Allow empty input.
            cursor: Cursor style when hovering.
            exportselection: Export selection to clipboard.
            font: Font for text display.
            foreground: Text color.
            initial_focus: If True, widget receives focus on creation.
            justify: Text alignment ('left', 'center', 'right').
            show_message: If True, displays message area.
            padding: Padding around entry widget.
            takefocus: If True, widget accepts Tab focus.
            textvariable: Tkinter Variable to link with text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal object for reactive updates.
            width: Width in characters.
            xscrollcommand: Callback for horizontal scrolling.
        """
        # Store before super().__init__ so property override is safe if called during init
        self._selection_mode = selection_mode
        self._range_value: tuple[date, date] | None = None
        self._value_format = value_format

        if picker_title is None:
            picker_title = "Select date range" if selection_mode == "range" else "Select new date"

        kwargs.setdefault('accent', 'primary')
        # In range mode pass value=None so the entry starts empty; display text
        # is set manually below after range initialisation.
        super().__init__(
            master=master,
            value=None if selection_mode == "range" else value,
            value_format=value_format,
            label=label,
            message=message,
            **kwargs,
        )

        # configuration
        self._show_picker_button = show_picker_button
        self._picker_title = picker_title
        self._picker_first_weekday = picker_first_weekday
        self._min_date = min_date
        self._max_date = max_date
        self._disabled_dates = disabled_dates

        self._button_pack = {}

        self.insert_addon(
            Button,
            position="after",
            name="date-picker",
            icon="calendar-week",
            icon_only=True,
            command=self._show_date_picker
        )

        self._delegate_show_picker_button(self._show_picker_button)

        if selection_mode == "range":
            # Make the entry readonly — user must use the picker
            self._entry.state(['readonly'])
            self._field.state(['!disabled'])

            # Seed initial range
            s = self._coerce_date(start_date)
            e = self._coerce_date(end_date)
            if s is not None and e is not None:
                self._set_range((s, e))

    # --- value property override for range mode -------------------------

    @property
    def value(self) -> date | tuple[date, date] | None:
        """Selected date (single mode) or `(start, end)` tuple (range mode)."""
        if self._selection_mode == 'range':
            return self._range_value
        return Field.value.fget(self)

    @value.setter
    def value(self, val):
        if self._selection_mode == 'range':
            self._set_range(val)
        else:
            Field.value.fset(self, val)

    # --- addon state override for range mode ----------------------------

    def _sync_addon_state(self, event=None):
        if getattr(self, '_selection_mode', 'single') == 'range':
            # Entry is intentionally readonly in range mode; keep addons active
            self._set_addons_state(False)
        else:
            super()._sync_addon_state(event)

    # --- range helpers --------------------------------------------------

    def _set_range(self, val) -> None:
        """Set the range value, update display text, and fire <<Change>>."""
        if val is None:
            prev = self._range_value
            self._range_value = None
            self.variable.set("")
            if prev is not None:
                try:
                    self._entry.event_generate("<<Change>>", data=ChangeEvent(
                        value=None, prev_value=prev, text="",
                    ))
                except Exception:
                    pass
            return

        if not (isinstance(val, (tuple, list)) and len(val) == 2):
            return

        s = self._coerce_date(val[0])
        e = self._coerce_date(val[1])
        if s is None or e is None:
            return
        if e < s:
            s, e = e, s

        prev = self._range_value
        self._range_value = (s, e)
        self.variable.set(self._format_range_display(s, e))

        if prev != self._range_value:
            try:
                self._entry.event_generate("<<Change>>", data=ChangeEvent(
                    value=self._range_value,
                    prev_value=prev,
                    text=self.variable.get(),
                ))
            except Exception:
                pass

    def _format_range_display(self, start: date, end: date) -> str:
        """Format a date range as 'Jan 1 – Jan 31, 2025' using value_format."""
        from bootstack.i18n import IntlFormatter, MessageCatalog
        fmt = IntlFormatter(locale=MessageCatalog.locale())
        start_str = fmt.format(start, self._value_format)
        end_str = fmt.format(end, self._value_format)
        return f"{start_str} – {end_str}"

    @staticmethod
    def _coerce_date(value) -> date | None:
        """Coerce a date/datetime/ISO-string to a date, or return None."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except Exception:
                    continue
            try:
                return datetime.fromisoformat(value).date()
            except Exception:
                return None
        return None

    # --- public properties ----------------------------------------------

    @property
    def date_picker_button(self) -> Button | None:
        """Get the calendar picker button widget."""
        return self.addons.get('date-picker')

    @configure_delegate('show_picker_button')
    def _delegate_show_picker_button(self, value: bool = None):
        """Get or set the visibility of the calendar picker button."""
        if value is None:
            return self._show_picker_button
        else:
            if value:
                if not self.date_picker_button.winfo_ismapped():
                    self.date_picker_button.pack(**self._button_pack)
            else:
                self._button_pack = self.date_picker_button.pack_info()
                self.date_picker_button.pack_forget()
        return None

    def _show_date_picker(self):
        """Open the calendar picker dialog.

        Opens a DateDialog seeded with the current value (or range), updates
        the entry when a date is picked, and leaves the field unchanged on
        cancel.
        """
        from bootstack.dialogs._impl.datedialog import DateDialog

        # Prevent multiple dialogs: reuse existing if still open
        existing = getattr(self, "_active_date_dialog", None)
        top = getattr(getattr(existing, "_dialog", None), "toplevel", None) if existing else None
        try:
            exists = bool(top and top.winfo_exists())
        except Exception:
            exists = False

        if exists:
            try:
                top.lift()
                top.focus_force()
            except Exception:
                pass
            return
        self._active_date_dialog = None

        if self._selection_mode == "range":
            cur = self._range_value
            dialog = DateDialog(
                master=self.winfo_toplevel(),
                title=self._picker_title,
                first_weekday=self._picker_first_weekday,
                selection_mode="range",
                start_date=cur[0] if cur else None,
                end_date=cur[1] if cur else None,
                accent=self._accent,
                disabled_dates=self._disabled_dates,
                min_date=self._min_date,
                max_date=self._max_date,
                hide_window_chrome=True,
                close_on_click_outside=False,
            )
        else:
            current_value = self.value
            if isinstance(current_value, datetime):
                current_value = current_value.date()
            if not isinstance(current_value, date):
                current_value = date.today()
            dialog = DateDialog(
                master=self.winfo_toplevel(),
                title=self._picker_title,
                first_weekday=self._picker_first_weekday,
                initial_date=current_value,
                accent=self._accent,
                disabled_dates=self._disabled_dates,
                min_date=self._min_date,
                max_date=self._max_date,
                hide_window_chrome=True,
                close_on_click_outside=False,
            )

        self._active_date_dialog = dialog

        def _on_result(payload):
            result = payload.get('result') if isinstance(payload, dict) else payload
            if self._selection_mode == "range":
                if isinstance(result, tuple) and len(result) == 2:
                    self.value = result
            else:
                if isinstance(result, (date, datetime)):
                    self.value = result

        dialog.on_result(lambda x: _on_result(x))
        dialog.show(
            anchor_to=self._field,
            anchor_point='se',
            window_point='ne',
            offset=(-4, 2),
        )

        top = getattr(getattr(dialog, "_dialog", None), "toplevel", None)
        cleared = False
        try:
            if top and top.winfo_exists():
                def _clear(_=None):
                    self._active_date_dialog = None
                top.bind("<Destroy>", _clear, add="+")
                cleared = True
        except Exception:
            cleared = False
        if not cleared:
            self._active_date_dialog = None

        # Fallback: ensure value is applied after modal dialog closes.
        selected = dialog.result
        if self._selection_mode == "range":
            if isinstance(selected, tuple) and len(selected) == 2:
                self.value = selected
        else:
            if isinstance(selected, datetime):
                selected = selected.date()
            if isinstance(selected, date):
                self.value = selected

        # Return focus to the entry after dialog closes
        # Note: focus_force() is needed on Windows after override-redirect dialogs
        try:
            self._entry.focus_force()
        except Exception:
            pass

    def _picker_position(self):
        """Choose a dialog position beneath the entry mirroring SelectBox spacing."""
        try:
            # The field is already rendered when the user clicks, so no layout
            # flush is needed — update_idletasks() here would drain unrelated
            # idle callbacks (e.g. Calendar._lock_size from a previous dialog)
            # and cause noticeable lag on repeated opens.
            field_widget = self._field
            x = field_widget.winfo_rootx() + 4
            y = field_widget.winfo_rooty() + field_widget.winfo_height() + 2
            return x, y
        except Exception:
            pass

        try:
            top = self.winfo_toplevel()
            x = top.winfo_rootx() + top.winfo_width() // 2
            y = top.winfo_rooty() + top.winfo_height() // 2
            return x, y
        except Exception:
            return None

