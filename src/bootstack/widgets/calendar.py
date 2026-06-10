from __future__ import annotations

from datetime import date, datetime
from typing import overload, Any, Callable, Iterable, Literal

from bootstack.widgets._impl.composites.calendar import Calendar as _InternalCalendar
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events
from bootstack.events import DateSelectEvent, Subscription
from bootstack.streams import Stream
from bootstack.widgets.types import AccentToken, Event, Padding


class Calendar(PublicWidgetBase):
    """An inline calendar for single-date or date-range selection.

    Always visible — not a popup. Displays one month in `'single'` mode and
    two months side-by-side in `'range'` mode.

    Dates can be passed as `datetime.date` objects, `datetime.datetime`
    objects, or ISO strings (`"2026-05-31"`).

    Args:
        value: Initially selected date (single mode only).
        start_date: Initially selected range start date (range mode).
        end_date: Initially selected range end date (range mode).
        disabled_dates: Dates that cannot be selected. Displayed with a
            strikethrough style.
        selection_mode: `'single'` (default) for one date; `'range'`
            for a start–end span.
        min_date: Earliest selectable date. Earlier dates are disabled
            and month navigation is blocked before this point.
        max_date: Latest selectable date. Later dates are disabled
            and month navigation is blocked past this point.
        show_outside_days: Show days from adjacent months in the grid.
            Defaults to `True` in single mode and `False` in range mode.
        show_week_numbers: Display ISO 8601 week numbers in the leftmost
            column. Defaults to `False`.
        first_weekday: First day of the week as an integer (0=Monday,
            6=Sunday). If omitted, the locale default is used.
        accent: Accent token applied to selected dates and highlights.
            Defaults to `'primary'`.
        padding: Space in pixels around the calendar grid.
        parent: Explicit parent widget. If omitted, the current
            context-stack container is used.
        **kwargs: Layout placement options applied by the parent container —
            `fill`, `expand`, `anchor`, `margin`, `row`, `column`, `sticky`.
            See :doc:`/tasks/layout`.
    """

    def __init__(
        self,
        *,
        value: date | datetime | str | None = None,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
        disabled_dates: Iterable[date | datetime | str] | None = None,
        selection_mode: Literal["single", "range"] = "single",
        max_date: date | datetime | str | None = None,
        min_date: date | datetime | str | None = None,
        show_outside_days: bool | None = None,
        show_week_numbers: bool = False,
        first_weekday: int | None = None,
        accent: AccentToken | str | None = None,
        padding: Padding | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        kw: dict[str, Any] = {"selection_mode": selection_mode, "show_week_numbers": show_week_numbers}
        if value is not None:
            kw["value"] = value
        if start_date is not None:
            kw["start_date"] = start_date
        if end_date is not None:
            kw["end_date"] = end_date
        if disabled_dates is not None:
            kw["disabled_dates"] = disabled_dates
        if max_date is not None:
            kw["max_date"] = max_date
        if min_date is not None:
            kw["min_date"] = min_date
        if show_outside_days is not None:
            kw["show_outside_days"] = show_outside_days
        if first_weekday is not None:
            kw["first_weekday"] = first_weekday
        if accent is not None:
            kw["accent"] = accent
        if padding is not None:
            kw["padding"] = padding

        self._internal = _InternalCalendar(tk_master, **kw)
        self._attach_to_parent(layout_kw)

    # ----- Value API -----

    @property
    def value(self) -> date | None:
        """The currently selected date."""
        return self._internal.value

    @value.setter
    def value(self, val: date | datetime | str | None) -> None:
        self._internal.value = val

    def get(self) -> date | None:
        """Return the currently selected date."""
        return self._internal.get()

    def set(self, value: date | datetime | str | None) -> None:
        """Set the selected date without emitting `<<DateSelect>>`."""
        self._internal.set(value)

    # ----- Range API -----

    @property
    def range(self) -> tuple[date | None, date | None]:
        """The selected date range as (start, end)."""
        return self._internal.range

    @range.setter
    def range(self, val: Any) -> None:
        self._internal.range = val

    def get_range(self) -> tuple[date | None, date | None]:
        """Return the selected date range."""
        return self._internal.get_range()

    def set_range(
        self,
        start: date | datetime | str | None,
        end: date | datetime | str | None = None,
    ) -> None:
        """Set the selected date range without emitting `<<DateSelect>>`."""
        self._internal.set_range(start, end)

    # ----- Events -----

    @overload
    def on_date_selected(self) -> Stream: ...
    @overload
    def on_date_selected(self, handler: Callable[[DateSelectEvent], Any]) -> Subscription: ...
    def on_date_selected(self, handler: Callable[[DateSelectEvent], Any] | None = None) -> Stream | Subscription:
        """Register a callback fired when a date or range is selected.

        In single mode the handler fires on every date click. In range mode
        it fires after each click — check `calendar.range` to see whether
        a complete range has been set (`end` is `None` while the second
        date is still pending).

        Args:
            handler: Called with a :class:`~bootstack.events.DateSelectEvent`.
                Omit to get a composable :class:`~bootstack.streams.Stream`
                instead.

        Returns:
            A cancellable :class:`~bootstack.events.Subscription` when a
            handler is given, otherwise a :class:`~bootstack.streams.Stream`.
        """
        return self.on("<<DateSelect>>", handler)


register_widget_events(Calendar, {})
