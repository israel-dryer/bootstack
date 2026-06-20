"""Time entry field widget with dropdown list of time intervals.

Provides a specialized entry field for time input with a searchable dropdown
list of time values at specified intervals.
"""

from __future__ import annotations

import datetime
from bootstack.i18n.intl_format import DateFormatSpec

from typing_extensions import Unpack

from bootstack._runtime.app import get_app_settings
from bootstack.i18n import IntlFormatter
from bootstack.widgets._impl.composites.field import FieldOptions
from bootstack.widgets._impl.composites.selectbox import SelectBox
from bootstack.widgets.types import Master


class TimeEntry(SelectBox):
    """Time entry field with dropdown list of time intervals.

    TimeEntry extends SelectBox to provide specialized time input with
    locale-aware formatting and a searchable dropdown of time intervals.
    The widget supports various time format presets and custom time patterns.
    """

    def __init__(
            self,
            master: Master = None,
            value: datetime.time | str = None,
            value_format: DateFormatSpec = 'shortTime',
            interval: int = 30,
            min_time: datetime.time | str = None,
            max_time: datetime.time | str = None,
            label: str = None,
            message: str = None,
            **kwargs: Unpack[FieldOptions]
    ):
        """Args:
            master: Parent widget. If None, uses the default root window.
            value: Initial time value to display. Can be a time object or string.
                Empty by default.
            value_format: Time format pattern for parsing and displaying times.
                Default is "shortTime" (e.g., "3:30 PM"). Common formats:
                "shortTime" (3:30 PM), "longTime" (3:30:45 PM PST),
                "mediumTime" (3:30:45 PM), "HH:mm" (15:30), "h:mm a" (3:30 PM).
            interval: Time interval in minutes for dropdown items (e.g., 15, 30, 60).
                Default is 30 minutes.
            min_time: Minimum time value for the dropdown list. Can be a time object
                or string (e.g., "09:00" or "9:00 AM"). Default is midnight (00:00).
            max_time: Maximum time value for the dropdown list. Can be a time object
                or string (e.g., "17:00" or "5:00 PM"). Default is 11:59 PM (23:59).
            label: Optional label text to display above the entry field.
                If required=True, an asterisk (*) is automatically appended.
            message: Optional message text to display below the entry field.
                Used for hints or help text. Replaced by validation errors when
                validation fails.

        Other Parameters:
            locale: Locale identifier for time formatting (e.g., 'en_US').
            required: If True, field cannot be empty.
            accent: Accent token for the focus ring and active border.
            allow_blank: Allow empty input.
            width: Width in characters.
            textvariable: Tkinter Variable to link with text.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            textsignal: Signal object for reactive updates.
        """
        self._interval = interval
        self._value_format = value_format
        self._locale = kwargs.get('locale') or get_app_settings().locale

        # Parse and store time range
        self._min_time = self._parse_time(min_time) if min_time else datetime.time(0, 0)
        self._max_time = self._parse_time(max_time) if max_time else datetime.time(23, 59)

        # An empty field stays empty — consistent with the other field widgets,
        # so `required=` meaningfully demands input (was: defaulted to the current
        # time, which silently pre-filled and defeated `required`). Pass an
        # explicit `value=` to seed a starting time.
        if value is None or value == "":
            formatted_value = ""
        else:
            # Normalize value to a time object using our own parser (avoids
            # dateparser mis-reading "08:30" as "August 30"), then format it with
            # the same IntlFormatter used to build items so the strings compare
            # equal.
            formatter = IntlFormatter(locale=self._locale)
            time_val = self._parse_time(value) if isinstance(value, str) else value
            formatted_value = formatter.format(time_val, value_format)

        # Generate time intervals for dropdown
        items = self._generate_time_intervals()

        # Initialize SelectBox with time-specific configuration
        super().__init__(
            master=master,
            value=formatted_value,
            value_format=value_format,
            items=items,
            allow_custom_values=True,
            enable_search=True,
            dropdown_button_icon='clock',
            message=message,
            label=label,
            **kwargs
        )

    def _parse_time(self, time_value: datetime.time | str) -> datetime.time:
        """Parse time value from various input formats.

        Args:
            time_value: Time value as time object or string

        Returns:
            Parsed time object, or midnight (00:00) if parsing fails
        """
        if isinstance(time_value, datetime.time):
            return time_value

        if isinstance(time_value, str):
            # Try 24-hour format (HH:MM)
            try:
                dt = datetime.datetime.strptime(time_value, '%H:%M')
                return dt.time()
            except ValueError:
                pass

            # Try 12-hour format (h:MM AM/PM)
            try:
                dt = datetime.datetime.strptime(time_value, '%I:%M %p')
                return dt.time()
            except ValueError:
                pass

        # Fallback to midnight
        return datetime.time(0, 0)

    def _generate_time_intervals(self) -> list[str]:
        """Generate list of formatted time strings at specified intervals.

        Creates a list of time values from min_time to max_time at the specified
        interval, formatted according to value_format. Uses IntlFormatter for
        consistent locale-aware formatting with Field.

        Returns:
            List of formatted time strings
        """
        times = []
        formatter = IntlFormatter(locale=self._locale)

        # Convert time objects to datetime for iteration
        current = datetime.datetime.combine(datetime.date.today(), self._min_time)
        end = datetime.datetime.combine(datetime.date.today(), self._max_time)

        # Handle midnight crossing (e.g., min_time=22:00, max_time=02:00)
        if end < current:
            end += datetime.timedelta(days=1)

        # Generate intervals
        while current <= end:
            # Format using IntlFormatter (consistent with TextEntryPart)
            # Note: Pass datetime (not time) as IntlFormatter expects it for Babel
            try:
                formatted_time = formatter.format(current, self._value_format)
            except:
                # Fallback to 24-hour format if formatting fails
                formatted_time = current.strftime('%H:%M')

            times.append(formatted_time)
            current += datetime.timedelta(minutes=self._interval)

        return times

