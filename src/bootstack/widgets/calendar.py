from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Iterable, Literal

from bootstack.widgets._impl.composites.calendar import Calendar as _InternalCalendar
from bootstack.widgets._impl.composites.calendar import DateSelectEventData
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events


class Calendar(PublicWidgetBase):
    """Inline calendar for single or range date selection.

    Args:
        value: Initial selected date (single mode).
        start_date: Range start date.
        end_date: Range end date. Only used when `selection_mode='range'`.
        disabled_dates: Dates that cannot be selected.
        selection_mode: `'single'` (default) or `'range'`.
        max_date: Maximum selectable date.
        min_date: Minimum selectable date.
        show_outside_days: Show days from adjacent months. Defaults to True
            for single mode, False for range mode.
        show_week_numbers: Display ISO week numbers in the leftmost column.
        first_weekday: First day of the week (0=Monday, 6=Sunday). Defaults
            to locale setting.
        accent: Accent token for selected dates and highlights.
        padding: Padding around the widget.
        parent: Override the context-stack parent.
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
        accent: str | None = None,
        padding: Any = None,
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

    def on_date_selected(self, handler: Callable) -> Any:
        """Register a callback for `<<DateSelect>>` events.

        Args:
            handler: Called when a date is selected or a range is updated.

        Returns:
            Subscription — call `.cancel()` to unsubscribe.
        """
        return self.on("<<DateSelect>>", handler)


register_widget_events(Calendar, {})
