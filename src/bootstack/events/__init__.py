"""Event objects, typed payloads, and subscriptions for bootstack widgets.

This package is the single catalog of every framework event shape:

- `Event` — the curated object handed to native/context handlers
  (click, hover, focus, resize, key, scroll).
- The payload dataclasses (`ChangeEvent`, `InputEvent`, …) — the
  *unpacked* objects handed to data-carrying handlers (`on_change`,
  `on_input`, `on_select`, …).
- `Subscription` — the cancellable handle that binding returns.
"""
from bootstack.events._event import Event
from bootstack.events._payloads import (
    AccordionChangeEvent,
    ButtonGroupClickEvent,
    ChangeEvent,
    ChangeKind,
    ChangeMethod,
    ChangeReason,
    DataChangeEvent,
    DateSelectEvent,
    DisplayModeEvent,
    ExportEvent,
    ImageErrorEvent,
    ImageLoadEvent,
    InputEvent,
    MenuSelectEvent,
    NavEvent,
    PageChangeEvent,
    PaneToggleEvent,
    RangeSliderCommitEvent,
    RangeSliderEvent,
    RowEvent,
    RowsEvent,
    ScrollEvent,
    SelectionEvent,
    SliderCommitEvent,
    SliderEvent,
    TabActivateEvent,
    TabChangeEvent,
    TabCloseEvent,
    TabDeactivateEvent,
    TabRef,
    TreeSelectionEvent,
    TextModifiedEvent,
    ToggleEvent,
    ValidationEvent,
    WorkspaceChangeEvent,
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
    # Payloads — picture / media
    "ImageLoadEvent",
    "ImageErrorEvent",
    # Payloads — navigation
    "PageChangeEvent",
    "NavEvent",
    "PaneToggleEvent",
    "DisplayModeEvent",
    "WorkspaceChangeEvent",
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
    "ExportEvent",
    # Payloads — tree
    "TreeSelectionEvent",
    # Payloads — text area
    "TextModifiedEvent",
    # Payloads — button group
    "ButtonGroupClickEvent",
    "MenuSelectEvent",
    # Payloads — data source
    "DataChangeEvent",
    "ChangeKind",
    # Payloads — scroll view
    "ScrollEvent",
]
