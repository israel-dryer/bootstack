"""Event objects, typed payloads, and subscriptions for bootstack widgets.

This package is the single catalog of every framework event shape:

- :class:`Event` — the curated object handed to native/context handlers
  (click, hover, focus, resize, key, scroll).
- The payload dataclasses (:class:`ChangeEvent`, :class:`InputEvent`, …) — the
  *unpacked* objects handed to data-carrying handlers (``on_change``,
  ``on_input``, ``on_select``, …).
- :class:`Subscription` — the cancellable handle that binding returns.
"""
from bootstack.events._event import Event
from bootstack.events._payloads import (
    AccordionChangeEvent,
    ButtonGroupClickEvent,
    ChangeEvent,
    ChangeMethod,
    ChangeReason,
    DateSelectEvent,
    DisplayModeEvent,
    InputEvent,
    NavEvent,
    PageChangeEvent,
    PaneToggleEvent,
    RangeSliderCommitEvent,
    RangeSliderEvent,
    RowEvent,
    RowsEvent,
    SelectionEvent,
    SliderCommitEvent,
    SliderEvent,
    TabActivateEvent,
    TabChangeEvent,
    TabCloseEvent,
    TabDeactivateEvent,
    TabRef,
    TextModifiedEvent,
    ToggleEvent,
    ValidationEvent,
)
from bootstack.events._subscription import Subscription

__all__ = [
    "Event",
    "Subscription",
    # Payloads — field / input
    "ChangeEvent",
    "InputEvent",
    "ValidationEvent",
    # Payloads — sliders & meters
    "SliderEvent",
    "SliderCommitEvent",
    "RangeSliderEvent",
    "RangeSliderCommitEvent",
    # Payloads — calendar
    "DateSelectEvent",
    # Payloads — expander / accordion
    "ToggleEvent",
    "AccordionChangeEvent",
    # Payloads — navigation
    "PageChangeEvent",
    "NavEvent",
    "PaneToggleEvent",
    "DisplayModeEvent",
    # Payloads — tabs
    "TabRef",
    "TabChangeEvent",
    "TabActivateEvent",
    "TabDeactivateEvent",
    "TabCloseEvent",
    "ChangeReason",
    "ChangeMethod",
    # Payloads — table
    "RowEvent",
    "RowsEvent",
    "SelectionEvent",
    # Payloads — text area
    "TextModifiedEvent",
    # Payloads — button group
    "ButtonGroupClickEvent",
]
