"""Typed event payloads — the catalog of every data-carrying framework event.

When a widget event carries application data (a new value, the typed text, a
validation result, a selected row), the handler bound with `on_*()` receives
one of the frozen dataclasses defined here, *unpacked* — the handler argument
IS the payload::

    field.on_change(lambda e: print(e.value, e.prev_value))
    field.on_input(lambda e: print(e.text))

Events that carry no payload (click, hover, focus, resize, key, scroll) instead
hand the handler a curated `Event`.

Every payload is `@dataclass(frozen=True, slots=True)` so attributes are
discoverable by editors and immutable in handlers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as _date
from typing import Any, Literal, Mapping

# ---------------------------------------------------------------------------
# Field / input family
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InputEvent:
    """Fires on every keystroke, before the value is committed.

    Use it for live feedback — character counts, as-you-type filtering. To react
    only once editing settles, use `on_change` instead.
    """

    text: str = ""
    """The current raw text in the field."""


@dataclass(frozen=True, slots=True)
class ChangeEvent:
    """Fires when a field's value is committed (on blur or Enter)."""

    value: Any = None
    """The committed, parsed value."""

    prev_value: Any = None
    """The value before this change."""

    text: str = ""
    """The raw display text behind the value."""


@dataclass(frozen=True, slots=True)
class ValidationEvent:
    """Fires after validation runs — `valid`, `invalid`, and `validate`."""

    value: Any = None
    """The value that was validated."""

    is_valid: bool = True
    """Whether validation passed."""

    message: str = ""
    """The failure message, or an empty string when valid."""


# ---------------------------------------------------------------------------
# Sliders & meters
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SliderEvent:
    """Fires while a slider (or gauge/meter) value moves."""

    value: float = 0.0
    """The new value."""

    prev_value: float = 0.0
    """The value before this move."""


@dataclass(frozen=True, slots=True)
class SliderCommitEvent:
    """Fires when a slider value is committed (drag released or stepped)."""

    value: float = 0.0
    """The committed value."""


@dataclass(frozen=True, slots=True)
class RangeSliderEvent:
    """Fires while either handle of a range slider moves."""

    low_value: float = 0.0
    """The new lower-bound value."""

    high_value: float = 0.0
    """The new upper-bound value."""

    prev_low_value: float = 0.0
    """The lower-bound value before this move."""

    prev_high_value: float = 0.0
    """The upper-bound value before this move."""


@dataclass(frozen=True, slots=True)
class RangeSliderCommitEvent:
    """Fires when a range slider's values are committed."""

    low_value: float = 0.0
    """The committed lower-bound value."""

    high_value: float = 0.0
    """The committed upper-bound value."""


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DateSelectEvent:
    """Fires when a date (or date range) is chosen in a calendar."""

    date: "_date | None" = None
    """The selected date."""

    range: "tuple[_date, _date] | None" = None
    """The selected `(start, end)` range, or `None` in single-date mode."""


# ---------------------------------------------------------------------------
# Expander / Accordion
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ToggleEvent:
    """Fires when an expander is expanded or collapsed."""

    expanded: bool = False
    """Whether the expander is now open."""


@dataclass(frozen=True, slots=True)
class AccordionChangeEvent:
    """Fires when an accordion's set of open panels changes."""

    expanded: tuple[Any, ...] = ()
    """The currently expanded panels."""


# ---------------------------------------------------------------------------
# Navigation — PageStack, SideNav
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PageChangeEvent:
    """Fires when the active page changes (mount, will-mount, change)."""

    page: str = ""
    """The key of the page now active."""

    prev_page: str | None = None
    """The key of the previously active page, or `None`."""

    nav: Any = None
    """Navigation direction/context for this transition, if any."""

    data: dict[str, Any] = field(default_factory=dict)
    """Arbitrary data passed to `navigate(key, data=...)`."""

    prev_data: Any = None
    """The data the previous page was navigated with."""

    index: int = 0
    """Position of this page in the navigation history."""

    length: int = 0
    """Total length of the navigation history."""

    can_back: bool = False
    """Whether there is a previous page to go back to."""

    can_forward: bool = False
    """Whether there is a next page to go forward to."""


@dataclass(frozen=True, slots=True)
class NavEvent:
    """Fires when a navigation item is selected."""

    key: str = ""
    """The key of the selected item."""


@dataclass(frozen=True, slots=True)
class PaneToggleEvent:
    """Fires when a navigation pane opens or closes."""

    is_open: bool = False
    """Whether the pane is now open."""


@dataclass(frozen=True, slots=True)
class DisplayModeEvent:
    """Fires when a navigation widget's display mode changes."""

    mode: Any = None
    """The new display mode."""


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

ChangeReason = Literal["user", "api", "hide", "forget", "unknown"]
ChangeMethod = Literal["click", "key", "programmatic", "unknown"]


@dataclass(frozen=True, slots=True)
class TabRef:
    """Identifies a tab by key and display text."""

    key: str = ""
    """The tab's stable key."""

    text: str = ""
    """The tab's display text."""


@dataclass(frozen=True, slots=True)
class TabChangeEvent:
    """Fires when the active tab changes."""

    current: TabRef | None = None
    """The tab now active."""

    previous: TabRef | None = None
    """The tab that was active before, or `None`."""

    reason: ChangeReason = "unknown"
    """Why the change happened."""

    via: ChangeMethod = "unknown"
    """How the change was triggered."""


@dataclass(frozen=True, slots=True)
class TabActivateEvent:
    """Fires when a tab becomes active."""

    key: str = ""
    """The activated tab's key."""

    text: str = ""
    """The activated tab's display text."""


@dataclass(frozen=True, slots=True)
class TabDeactivateEvent:
    """Fires when a tab stops being active."""

    key: str = ""
    """The deactivated tab's key."""

    text: str = ""
    """The deactivated tab's display text."""


@dataclass(frozen=True, slots=True)
class TabCloseEvent:
    """Fires when a tab's close button is used."""

    value: Any = None
    """The closed tab's value/key."""


# ---------------------------------------------------------------------------
# Table — row-oriented
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RowEvent:
    """Fires for a single-row action (click, double-click, right-click)."""

    record: dict[str, Any] = field(default_factory=dict)
    """The row's record."""

    id: Any = None
    """The row's id."""


@dataclass(frozen=True, slots=True)
class RowsEvent:
    """Fires for a multi-row action (insert, update, delete, move)."""

    records: list[dict[str, Any]] = field(default_factory=list)
    """The affected records."""


@dataclass(frozen=True, slots=True)
class SelectionEvent:
    """Fires when the set of selected rows changes."""

    records: list[dict[str, Any]] = field(default_factory=list)
    """The selected records."""

    ids: list[Any] = field(default_factory=list)
    """The selected rows' ids."""


@dataclass(frozen=True, slots=True)
class ExportEvent:
    """Fires after the table's data is exported (copied or saved)."""

    count: int = 0
    """The number of rows exported."""

    target: str = ""
    """Where the data went — `'clipboard'` or `'file'`."""

    format: str = ""
    """The format written — `'csv'`, `'tsv'`, or `'xlsx'`."""

    path: str | None = None
    """The destination file path when `target` is `'file'`, else `None`."""

    records: list[dict[str, Any]] = field(default_factory=list)
    """The exported records. Populated for in-memory targets (clipboard);
    empty for streamed file exports, which never materialize all rows."""


# ---------------------------------------------------------------------------
# Tree — node-oriented
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TreeSelectionEvent:
    """Fires when a tree's set of selected nodes changes."""

    nodes: list[Any] = field(default_factory=list)
    """The selected `TreeNode` handles, in tree order."""


# ---------------------------------------------------------------------------
# TextArea / CodeEditor
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TextModifiedEvent:
    """Fires when a text area's modified (dirty) flag changes."""

    is_dirty: bool = False
    """Whether the text differs from the last saved/baseline content."""


# ---------------------------------------------------------------------------
# ButtonGroup
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ButtonGroupClickEvent:
    """Fires when a button in a button group is clicked."""

    key: str = ""
    """The clicked button's key."""

    text: str = ""
    """The clicked button's label text."""

    icon: Any = None
    """The clicked button's icon, if any."""


# ---------------------------------------------------------------------------
# Data source — change broadcasting
# ---------------------------------------------------------------------------


ChangeKind = Literal[
    "load",
    "insert",
    "update",
    "delete",
    "move",
    "filter",
    "sort",
    "reload",
    "select",
]
"""What kind of change a `DataChangeEvent` describes.

A row mutation (`insert`/`update`/`delete`/`move`), a view change
(`filter`/`sort`), a bulk replace (`load`/`reload`), or a selection toggle
(`select`).
"""


@dataclass(frozen=True, slots=True)
class DataChangeEvent:
    """Broadcast by a data source when its data or view changes.

    Delivered to handlers registered with `DataSource.on_change`. Because the
    source coalesces rapid mutations into one notification per event-loop turn,
    a single event may stand in for several underlying changes; in that case
    `kind` is `reload` and the per-row fields are empty. Treat it as a coarse
    "something changed" signal and re-read the source for current data.
    """

    kind: ChangeKind = "reload"
    """What changed."""

    id: Any = None
    """Affected record id for single-row kinds; `None` otherwise."""

    ids: tuple[Any, ...] = ()
    """Affected record ids for bulk kinds (e.g. `select_all`); empty otherwise."""

    record: Mapping[str, Any] | None = None
    """The affected record (or the applied updates) where cheaply available on
    `insert`/`update`; `None` otherwise."""
