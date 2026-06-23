"""TableView widget backed by an in-memory SQLite datasource.

The datasource performs filtering, sorting, and pagination while the widget
renders the current page in a Treeview with optional grouping, striping, and
context menus.
"""

from __future__ import annotations

import contextlib
import logging
import os
from collections import OrderedDict
from tkinter import font as tkfont

from typing import Any, Callable
from typing_extensions import Literal, TypedDict, Unpack

from bootstack.widgets.types import Master, WidgetDensity

from bootstack.events import RowEvent, RowsEvent, SelectionEvent, ExportEvent
from bootstack._core.images import _ImageService
from bootstack.style.style import get_style
# Row identity and the set of hidden internal columns are read through the
# datasource's protocol-level helpers (`_record_id`, `_public_record`,
# `_internal_fields`) so the table works with any `DataSourceProtocol` source,
# not just SqliteDataSource. SqliteDataSource is imported only to create the
# default in-memory source when no `datasource=` is supplied.
from bootstack.data.sqlite_source import SqliteDataSource
from bootstack.data.query import col, any_of, all_of
from bootstack.widgets._impl.primitives.button import Button
from bootstack._runtime.utility import bind_right_click
from bootstack.widgets._impl.composites.contextmenu import ContextMenu
from bootstack.widgets._impl.composites.tooltip import ToolTip
from bootstack.widgets._impl.composites.dropdownbutton import DropdownButton
from bootstack.widgets._impl.primitives.entry import Entry
from bootstack.widgets._impl.primitives.frame import Frame, FrameKwargs
from bootstack.widgets._impl.primitives.label import Label
from bootstack.widgets._impl.primitives.scrollbar import Scrollbar
from bootstack.widgets._impl.primitives.progressbar import Progressbar
from bootstack.widgets._impl.composites.selectbox import SelectBox
from bootstack.widgets._impl.primitives.separator import Separator
from bootstack.widgets._impl.composites.textentry import TextEntry
from bootstack.widgets._impl.primitives.treeview import TreeView
from bootstack.i18n import MessageCatalog

from .types import (
    parse_selection_mode as _parse_selection_mode,
    build_editing_options as _build_editing_options,
    build_selection_options as _build_selection_options,
    build_filtering_options as _build_filtering_options,
    build_exporting_options as _build_exporting_options,
    build_paging_options as _build_paging_options,
    build_search_options as _build_search_options,
    build_row_alternation_options as _build_row_alternation_options,
)

logger = logging.getLogger(__name__)

# Max characters of the filter summary shown in the status bar before it is
# truncated (the full text is then revealed via a hover tooltip).
_FILTER_STATUS_MAXLEN = 48

# Read-batch size when streaming an export (a throughput knob, distinct from the
# on-screen page size).
_EXPORT_CHUNK_SIZE = 1000

# Soft cap for the materializing accessors (to_rows/to_csv); above this they
# raise and point the caller at the streaming API.
_EXPORT_MAX_MATERIALIZE = 100_000

# Above this row count the built-in "Save to file" runs asynchronously with a
# progress dialog; below it, a synchronous (instant) write.
_EXPORT_ASYNC_THRESHOLD = 5000

# Stripe strength: fraction of the elevated stripe color blended over the table
# surface (lower = fainter stripe). Tuned so the stripe stays a faint neutral
# that contrasts with the subtle accent selection.
_STRIPE_STRENGTH = 0.5

# Fixed pixel size for per-row selection marker icons (checkbox/dot). Rendered
# 1:1 into the row's icon slot — kept even and unscaled for crisp edges.
_MARKER_ICON_SIZE = 20

# The toolbar and footer are utility chrome around the data, so their widgets are
# always compact regardless of the table's row density.
_CHROME_DENSITY: WidgetDensity = 'compact'

# Group expand/collapse chevrons shown in the leading slot of group-header rows
# (the native tree indicator was removed from the item layout).
_GROUP_OPEN_ICON = 'chevron-down'    # expanded
_GROUP_CLOSED_ICON = 'chevron-right'  # collapsed


class _ExportJob:
    """Drives a streamed export across the Tk event loop (cooperative chunking).

    Each idle tick writes one chunk and reschedules, so the UI stays responsive
    and the export can be cancelled between chunks. No worker threads — the
    data source's SQLite connection is thread-affine.
    """

    def __init__(self, widget, chunks, write_chunk, close, total, *, on_progress, on_complete):
        self._widget = widget            # provides after_idle / after_cancel
        self._chunks = chunks            # iterator of raw-record chunks
        self._write_chunk = write_chunk
        self._close = close
        self._total = total
        self._on_progress = on_progress
        self._on_complete = on_complete  # (status, written, error)
        self._written = 0
        self._cancelled = False
        self._done = False
        self._after_id = None

    def start(self) -> "_ExportJob":
        self._after_id = self._widget.after_idle(self._step)
        return self

    def cancel(self) -> None:
        """Request cancellation; takes effect before the next chunk."""
        self._cancelled = True

    def abort(self) -> None:
        """Cancel and close the writer NOW (used on widget teardown).

        Unlike `cancel()`, this doesn't wait for the next idle tick — the
        scheduled step won't run after destroy — so it closes the writer and
        finalizes synchronously.
        """
        if self._after_id is not None:
            try:
                self._widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._cancelled = True
        self._finish("cancelled", None)

    def _step(self) -> None:
        self._after_id = None
        if self._cancelled:
            self._finish("cancelled", None)
            return
        try:
            chunk = next(self._chunks, None)
        except Exception as exc:  # data-source read failed
            self._finish("error", exc)
            return
        if chunk is None:
            self._finish("completed", None)
            return
        try:
            self._write_chunk(chunk)
        except Exception as exc:
            self._finish("error", exc)
            return
        self._written += len(chunk)
        if self._on_progress is not None:
            try:
                self._on_progress(self._written, self._total)
            except Exception:
                logger.exception("Export progress callback failed")
        self._after_id = self._widget.after_idle(self._step)

    def _finish(self, status: str, error) -> None:
        if self._done:  # guard against double-finish (e.g. abort after natural end)
            return
        self._done = True
        try:
            self._close()
        except Exception:
            logger.exception("Failed to close export writer")
        if self._on_complete is not None:
            self._on_complete(status, self._written, error)


def _has_xlsxwriter() -> bool:
    """Whether the optional XlsxWriter dependency (bootstack[excel]) is installed."""
    return _module_available("xlsxwriter")


def _module_available(module: str) -> bool:
    """Whether an optional dependency can be imported."""
    import importlib.util
    try:
        return importlib.util.find_spec(module) is not None
    except Exception:
        return False


# Export formats the DataTable can offer. `kind` picks the engine: 'cooperative'
# uses the column-aware, cancelable, chunk-by-chunk exporter (good for huge CSVs);
# 'registry' streams through bootstack.data.writers (synchronous). `extra` names
# the pip extra to install when `available` is False.
_EXPORT_FORMATS: dict = {
    "csv":     {"ext": ".csv",     "label": "CSV file",        "kind": "cooperative", "extra": None,      "available": lambda: True},
    "tsv":     {"ext": ".tsv",     "label": "TSV file",        "kind": "cooperative", "extra": None,      "available": lambda: True},
    "xlsx":    {"ext": ".xlsx",    "label": "Excel file",      "kind": "cooperative", "extra": "excel",   "available": _has_xlsxwriter},
    "json":    {"ext": ".json",    "label": "JSON file",       "kind": "registry",    "extra": None,      "available": lambda: True},
    "jsonl":   {"ext": ".jsonl",   "label": "JSON Lines file", "kind": "registry",    "extra": None,      "available": lambda: True},
    "xml":     {"ext": ".xml",     "label": "XML file",        "kind": "registry",    "extra": None,      "available": lambda: True},
    "parquet": {"ext": ".parquet", "label": "Parquet file",    "kind": "registry",    "extra": "parquet", "available": lambda: _module_available("pyarrow")},
    "feather": {"ext": ".feather", "label": "Feather file",    "kind": "registry",    "extra": "parquet", "available": lambda: _module_available("pyarrow")},
    "hdf5":    {"ext": ".h5",      "label": "HDF5 file",       "kind": "registry",    "extra": "hdf5",    "available": lambda: _module_available("tables")},
}

# Map a file extension to a canonical export format name (including aliases).
_EXT_TO_EXPORT_FORMAT: dict = {spec["ext"]: name for name, spec in _EXPORT_FORMATS.items()}
_EXT_TO_EXPORT_FORMAT.update({
    ".ndjson": "jsonl",
    ".hdf5": "hdf5",
    ".hdf": "hdf5",
    ".arrow": "feather",
    ".txt": "csv",
})

_TABLE_SEARCH_MODE_OPTIONS = [
    ("table.search_mode_equals", "EQUALS"),
    ("table.search_mode_contains", "CONTAINS"),
    ("table.search_mode_starts_with", "STARTS WITH"),
    ("table.search_mode_ends_with", "ENDS WITH"),
]











class TableView(Frame):
    """TableView backed by an in-memory SqliteDataSource.

    Provides sortable headers, filtering/search, pagination or virtual scrolling,
    optional grouping, column striping, and configurable exporting/editing.

    """

    def __init__(
            self,
            master: Master = None,
            # Core data
            columns: list[str | dict] | None = None,
            rows: list | None = None,
            datasource: SqliteDataSource | None = None,
            # Selection & sorting
            selection_mode: Literal['none', 'single', 'multi'] = 'single',
            allow_select_all: bool = True,
            sorting_mode: Literal['single', 'none'] = 'single',
            # Filtering & search
            enable_filtering: bool = True,
            enable_header_filtering: bool = True,
            enable_row_filtering: bool = True,
            enable_search: bool = True,
            broadcast_search: bool = False,
            search_mode: Literal['standard', 'advanced'] = 'standard',
            search_trigger: Literal['enter', 'input'] = 'enter',
            # Paging & scrolling
            paging_mode: Literal['standard', 'virtual'] = 'standard',
            page_size: int = 25,
            page_index: int = 0,
            page_cache_size: int = 3,
            show_vscrollbar: bool = True,
            show_hscrollbar: bool = False,
            # Editing
            enable_adding: bool = False,
            enable_editing: bool = False,
            enable_deleting: bool = False,
            form_options: dict | None = None,
            # Exporting
            enable_exporting: bool = False,
            allow_export_selection: bool = True,
            export_scope: Literal['page', 'all'] = 'page',
            export_formats: tuple[str, ...] | None = None,
            # Appearance & extras
            striped: bool = False,
            striped_background: str = 'background[+0.85]',
            density: WidgetDensity = 'default',
            allow_grouping: bool = False,
            show_table_status: bool = True,
            show_column_chooser: bool = False,
            show_selection_controls: bool = False,
            id_field: str = "id",
            context_menus: Literal['none', 'headers', 'rows', 'all'] = 'all',
            column_min_width: int = 40,
            column_auto_width: bool = False,
            **kwargs: Unpack[FrameKwargs],
    ):
        """
        Create a TableView backed by an in-memory SqliteDataSource.

        Args:
            master: Parent widget.
            columns: Column definitions (list of strings or dicts with keys like
                "text", "key", "width", "minwidth").
            rows: Initial data to load (list of dicts or row-like sequences).
            datasource: Custom SqliteDataSource; if omitted, an in-memory source is created.
            selection_mode: Selection mode ('none', 'single', 'multi'). Defaults to 'single'.
            allow_select_all: Whether select-all is allowed. Defaults to True.
            sorting_mode: Sorting mode ('single' or 'none'). Defaults to 'single'.
            enable_filtering: Enable filtering features. Defaults to True.
            enable_header_filtering: Show filter option in header context menu. Defaults to True.
            enable_row_filtering: Show filter option in row context menu. Defaults to True.
            enable_search: Show search bar. Defaults to True.
            search_mode: Search mode ('standard' or 'advanced'). Defaults to 'standard'.
            search_trigger: When to trigger search ('enter' or 'input'). Defaults to 'enter'.
            paging_mode: Paging mode ('standard' or 'virtual'). Defaults to 'standard'.
            page_size: Number of rows per page. Defaults to 25.
            page_index: Initial page index. Defaults to 0.
            page_cache_size: Number of pages to cache. Defaults to 3.
            show_vscrollbar: Show vertical scrollbar. Defaults to True.
            show_hscrollbar: Show horizontal scrollbar. Defaults to False.
            enable_adding: Allow adding new rows. Defaults to False.
            enable_editing: Allow editing existing rows. Defaults to False.
            enable_deleting: Allow deleting rows. Defaults to False.
            form_options: Options dict for the edit form dialog.
            enable_exporting: Enable export functionality. Defaults to False.
            allow_export_selection: Allow exporting selected rows. Defaults to True.
            export_scope: Export scope ('page' or 'all'). Defaults to 'page'.
            export_formats: Tuple of export formats (e.g., ('csv', 'xlsx')).
            striped: Show alternating row colors. Defaults to False.
            striped_background: Background color for striped rows. Defaults to 'background[+0.85]'.
            density: Row compactness ('default' or 'compact'). Defaults to 'default'.
            allow_grouping: Allow grouping rows via header context menu. Defaults to False.
            show_table_status: Show filter/sort/group status labels and pager. Defaults to True.
            show_column_chooser: Show column chooser button. Defaults to False.
            show_selection_controls: Show per-row checkboxes in 'multi' selection
                mode (a plain click then toggles rows). No effect in 'single'
                mode or while grouped. Defaults to False.
            id_field: Record field used as the stable row identity for the
                auto-created data source. Ignored when `datasource` is provided.
                Defaults to 'id'.
            context_menus: Context menu visibility ('none', 'headers', 'rows', 'all').
                Defaults to 'all'.
            column_min_width: Global minimum width for columns. Defaults to 40.
            column_auto_width: Automatically size columns to widest visible text.
                Defaults to False.
            **kwargs: Additional arguments passed through to Frame.
        """
        super().__init__(master, **kwargs)

        # Build internal configuration dicts from flattened kwargs
        self._editing = _build_editing_options(
            enable_adding=enable_adding,
            enable_editing=enable_editing,
            enable_deleting=enable_deleting,
            form_options=form_options,
        )
        self._paging = _build_paging_options(
            paging_mode=paging_mode,
            page_size=page_size,
            page_index=page_index,
            page_cache_size=page_cache_size,
            show_vscrollbar=show_vscrollbar,
            show_hscrollbar=show_hscrollbar,
        )
        self._exporting = _build_exporting_options(
            enable_exporting=enable_exporting,
            allow_export_selection=allow_export_selection,
            export_scope=export_scope,
            export_formats=export_formats,
        )
        self._warn_unavailable_export_formats()
        self._filtering = _build_filtering_options(
            enable_filtering=enable_filtering,
            enable_header_filtering=enable_header_filtering,
            enable_row_filtering=enable_row_filtering,
        )
        self._selection = _build_selection_options(
            selection_mode=selection_mode,
            allow_select_all=allow_select_all,
        )
        self._searchbar = _build_search_options(
            enable_search=enable_search,
            search_mode=search_mode,
            search_trigger=search_trigger,
        )
        # The active free-text search term (composed with column filters into where()).
        self._search_text: str = ""
        # Tooltip showing the full filter summary when the status label is truncated.
        self._filter_tooltip: ToolTip | None = None
        # In-flight async export jobs, aborted on widget teardown.
        self._export_jobs: set = set()
        # The live add/edit form dialog while it is open (for capture/automation).
        self._active_form_dialog = None
        self._active_chooser_dialog = None
        self._row_alternation = _build_row_alternation_options(
            striped=striped,
            striped_background=striped_background,
        )
        # Treeview row density, forwarded to the TreeView style options.
        self._density: WidgetDensity = density
        # Per-row selection markers (checkbox/dot) in the leading icon slot.
        self._selection_indicators = bool(show_selection_controls)
        # Cache of rendered marker icons keyed by (name, size, color).
        self._marker_icons: dict = {}

        self._search_mode_map: dict[str, str] = {}
        self._broadcast_search: bool = broadcast_search
        # Suppress the table's own _on_source_change re-load while a broadcast
        # search is being applied (the load is done directly in _apply_where).
        self._suppressing_search_broadcast: bool = False
        self._sorting = sorting_mode
        self._show_table_status = show_table_status
        self._show_column_chooser = show_column_chooser
        self._allow_grouping = allow_grouping
        self._context_menus = (context_menus or 'all').lower()
        self._column_min_width = max(0, column_min_width)
        self._column_auto_width = column_auto_width
        self._datasource = datasource or SqliteDataSource(
            ':memory:', page_size=self._paging['page_size'], id_field=id_field
        )

        self._page_cache: OrderedDict[int, list[dict]] = OrderedDict()
        self._column_defs = columns or []
        self._column_keys: list[str] = []
        self._heading_texts: list[str] = []
        self._sort_state: dict[str, bool] = {}  # key -> ascending
        self._current_page = self._paging['page_index']
        self._loading_next = False
        self._heading_fg: str | None = None
        self._icon_sort_up = None
        self._icon_sort_down = None
        self._column_anchors: list[str] = []
        self._column_formats: dict[int, Any] = {}  # idx -> resolved display formatter (or None)
        self._column_filters: dict[str, list] = {}  # key -> list of allowed values
        self._column_types: dict[str, str] = {}
        self._alignment_sample: list[dict] | None = None
        self._row_map: dict[str, dict] = {}
        self._row_menu: ContextMenu | None = None
        # The row a right-click context menu targets. Right-click never changes
        # the selection (that is a left-click affordance), so the row menu acts
        # on this clicked row instead — see `_context_iids`.
        self._context_iid: str | None = None
        self._display_columns: list[int] = []
        self._header_menu: ContextMenu | None = None
        self._header_menu_col: int | None = None
        self._row_menu_col: int | None = None
        self._cached_total_count: int | None = None
        self._group_by_key: str | None = None
        self._group_parents: dict[str | None, str] = {}
        self._hidden_rows: dict[str, tuple[str, int]] = {}

        self._resolve_column_keys()

        seeded_records: list[dict] | None = None
        if rows:
            # Seed the source silently — the table renders this data itself below,
            # and the change subscription is not yet attached.
            with self._silence_source():
                try:
                    if self._column_keys:
                        # Avoid per-row dict conversion when we already know the column order
                        self._datasource.load(rows, column_keys=self._column_keys)
                        seeded_records = None
                    else:
                        seeded_records = self._to_records(rows)
                        self._datasource.load(seeded_records)
                except Exception:
                    # Last-resort fallback to dict conversion if direct load fails
                    seeded_records = self._to_records(rows)
                    try:
                        self._datasource.load(seeded_records)
                    except Exception:
                        seeded_records = []

        self._ensure_column_metadata(seeded_records)

        # UI
        self._build_toolbar()
        self._build_tree()
        if self._show_table_status or not self._paging['mode'] == 'virtual':
            self._build_footer()

        # Initial load
        self._load_page(0)

        # Auto-refresh when the data source changes from the outside (a shared
        # source mutated directly, or a background-thread feed). Every mutation
        # this table makes itself is wrapped in `_silence_source()`, so this
        # handler only fires for genuinely external changes. The hub marshals
        # the callback onto the main thread.
        self._change_sub = None
        on_change = getattr(self._datasource, 'on_change', None)
        if callable(on_change):
            try:
                self._change_sub = on_change(self._on_source_change)
            except Exception:
                self._change_sub = None
        self.bind('<Destroy>', self._on_table_destroy, add='+')
        # The alternating-row stripe is applied via imperative tag colors, which
        # are NOT refreshed by the ttk style rebuild. Re-apply on a theme change —
        # gated to on-screen by the Frame base hook (an off-screen table defers
        # its per-row repaint to <Map>), and released on destroy automatically.
        self._enable_theme_repaint(self._on_theme_changed)

    def _silence_source(self):
        """Context manager suppressing source change broadcasts for our own writes."""
        silence = getattr(self._datasource, '_silence', None)
        if callable(silence):
            return silence()
        return contextlib.nullcontext()

    @contextlib.contextmanager
    def _apply_view_to_source(self):
        """Temporarily apply this table's local filter/sort to the source (silenced).

        Saves the source's current where/order state, applies the table's own
        search + column-filter condition and sort order for the duration of the
        block, then restores the source to its original state. This lets each
        DataTable maintain independent view state over a shared source without
        permanently mutating it.
        """
        ds = self._datasource
        old_filter = getattr(ds, '_filter', None)
        old_sort = list(getattr(ds, '_sort', []))
        # Combine the source's own filter with this table's local search/column
        # filters so source-level constraints (e.g. ds.where(...) called from
        # app code) are respected alongside the table's per-view state.
        # When broadcast_search is on the table already wrote its search condition
        # to the source, so old_filter IS the combined condition — don't add local
        # conditions again or they'd be applied twice.
        if self._broadcast_search:
            combined = old_filter
        else:
            combined = all_of(
                old_filter,
                self._build_search_condition(),
                self._build_column_filter_condition(),
            )
        # Use the table's local sort when set; fall back to the source's sort
        # so a source-level order() is respected when no column header is clicked.
        sort_args = [k if asc else f"-{k}" for k, asc in self._sort_state.items()]
        effective_sort = sort_args if sort_args else old_sort
        with self._silence_source():
            ds.where(combined)
            ds.order(*effective_sort)
        try:
            yield
        finally:
            with self._silence_source():
                try:
                    ds.where(old_filter)
                finally:
                    ds.order(*old_sort)

    def _on_source_change(self, event=None) -> None:
        """Reload the current page after an external data-source change."""
        if self._suppressing_search_broadcast:
            # Consume the suppression — this is the hub flush that the broadcast
            # write in _apply_where() triggered. The table already loaded page 0
            # directly, so skip the redundant reload but allow future changes
            # through by clearing the flag.
            self._suppressing_search_broadcast = False
            return
        try:
            self._clear_cache()
            self._load_page(self._current_page)
        except Exception:
            logger.exception("Failed to reload table after data-source change")

    def _on_table_destroy(self, event=None) -> None:
        """Release subscriptions, in-flight exports, and the tooltip on destroy."""
        if event is not None and getattr(event, 'widget', None) is not self:
            return
        # The theme subscription is released by the Frame base hook's own
        # <Destroy> handler (publisher unsubscribe).
        sub = self._change_sub
        self._change_sub = None
        if sub is not None:
            try:
                sub.cancel()
            except Exception:
                pass
        # Abort any in-flight async export: its idle step won't run post-destroy,
        # so close the writer + remove the partial file synchronously now.
        for job in list(self._export_jobs):
            try:
                job.abort()
            except Exception:
                logger.exception("Failed to abort export job on destroy")
        self._export_jobs.clear()
        # Tear down the filter tooltip (unbinds its handlers, cancels its timer).
        tooltip = self._filter_tooltip
        self._filter_tooltip = None
        if tooltip is not None:
            try:
                tooltip.destroy()
            except Exception:
                pass

    # ------------------------------------------------------------------ Public API
    def set_data(self, rows: list) -> None:
        """Replace data in the datasource and refresh the grid."""
        with self._silence_source():
            if self._column_keys:
                self._datasource.load(rows, column_keys=self._column_keys)
                seeded_records = None
            else:
                seeded_records = self._to_records(rows)
                self._datasource.load(seeded_records)
        self._ensure_column_metadata(seeded_records)
        self._clear_cache()
        self._alignment_sample = None  # re-sample for column alignment on new data
        self._load_page(0)

    # ------------------------------------------------------------------ Public data/selection API
    def _public_record(self, rec: dict | None) -> dict:
        """Return a user-facing copy of `rec` — internal columns stripped, `id` surfaced."""
        return self._datasource._public_record(rec)

    def _record_id(self, rec: dict | None) -> Any:
        """Stable identity of a raw record, via the datasource's id accessor."""
        return self._datasource._record_id(rec) if rec else None

    def _internal_fields(self) -> "frozenset[str]":
        """Raw-record keys the datasource treats as internal (hidden from users)."""
        return self._datasource._internal_fields()

    def _iid_for_id(self, rid: Any) -> str | None:
        """Find the row handle of a currently-rendered row by its record `id`."""
        for iid, rec in self._row_map.items():
            if self._record_id(rec) == rid:
                return iid
        return None

    @property
    def selected_rows(self) -> list[dict]:
        """List of record dicts for the current selection."""
        rows: list[dict] = []
        for iid in self._tree.selection():
            if iid in self._row_map:
                rows.append(self._public_record(self._row_map[iid]))
        return rows

    # ------------------------------------------------------------------ Public row/column manipulation
    def insert_rows(self, rows: list) -> None:
        """Insert new rows via the datasource and refresh."""
        recs = self._to_records(rows)
        inserted: list[dict] = []
        with self._silence_source():
            for rec in recs:
                try:
                    # Strip any public 'id' — the datasource assigns the id.
                    payload = {k: v for k, v in dict(rec).items() if k != "id"}
                    new_id = self._datasource.insert(payload)
                    record = self._public_record(payload)
                    if new_id is not None:
                        record["id"] = new_id
                    inserted.append(record)
                except Exception:
                    logger.exception("Failed to insert record")
        if inserted:
            self._clear_cache()
            self._load_page(self._current_page)
            self.event_generate("<<RowsInsert>>", data=RowsEvent(records=inserted))

    def update_rows(self, rows: list[dict]) -> None:
        """Update rows by record `id`; each dict must include an `id` key."""
        updated: list[dict] = []
        with self._silence_source():
            for rec in rows:
                rec_id = rec.get("id")
                if rec_id is None:
                    continue
                _hidden = self._internal_fields()
                updates = {k: v for k, v in rec.items() if k != "id" and k not in _hidden}
                try:
                    self._datasource.update(rec_id, updates)
                    updated.append(dict(rec))
                except Exception:
                    logger.exception("Failed to update record id=%s", rec_id)
        if updated:
            self._clear_cache()
            self._load_page(self._current_page)
            self.event_generate("<<RowsUpdate>>", data=RowsEvent(records=updated))

    def delete_rows(self, rows_or_ids: list) -> None:
        """Delete rows by record `id`, or by record dicts containing an `id` key."""
        deleted: list[dict] = []
        with self._silence_source():
            for item in rows_or_ids:
                rec_id = None
                rec = {}
                if isinstance(item, dict):
                    rec = dict(item)
                    rec_id = item.get("id")
                else:
                    rec_id = item
                if rec_id is None:
                    continue
                try:
                    self._datasource.delete(rec_id)
                    if not rec:
                        rec = {"id": rec_id}
                    deleted.append(rec)
                except Exception:
                    logger.exception("Failed to delete record id=%s", rec_id)
        if deleted:
            self._clear_cache()
            self._load_page(self._current_page)
            self.event_generate("<<RowsDelete>>", data=RowsEvent(records=deleted))

    def insert_columns(self, *_args, **_kwargs) -> None:
        """Not currently supported; columns are defined at construction time."""
        raise NotImplementedError("Dynamic column insertion is not supported yet")

    def delete_columns(self, indices: list[int]) -> None:
        """Hide columns at the given indices."""
        self.hide_columns(indices)

    def move_rows(self, iids: list[str], to_index: int) -> None:
        """Move the given rows to a target index in the root list."""
        children = list(self._tree.get_children(""))
        to_index = max(0, min(len(children), to_index))
        for offset, iid in enumerate(iids):
            try:
                self._tree.move(iid, "", to_index + offset)
            except Exception:
                pass
        self._apply_row_alternation()
        moved_recs = [self._row_map.get(i) for i in iids if i in self._row_map]
        if moved_recs:
            records = [self._public_record(r) for r in moved_recs]
            self.event_generate("<<RowsMove>>", data=RowsEvent(records=records))

    def move_columns(self, from_index: int, to_index: int) -> None:
        """Reorder a column from one index to another."""
        if from_index < 0 or from_index >= len(self._display_columns):
            return
        to_index = max(0, min(len(self._display_columns) - 1, to_index))
        col_id = self._display_columns.pop(from_index)
        self._display_columns.insert(to_index, col_id)
        self._tree.configure(displaycolumns=self._display_columns)

    def hide_rows(self, iids: list[str]) -> None:
        """Hide rows from view (not removed from datasource)."""
        for iid in iids:
            try:
                parent = self._tree.parent(iid)
                children = list(self._tree.get_children(parent))
                idx = children.index(iid)
                self._hidden_rows[iid] = (parent, idx)
                self._tree.detach(iid)
            except Exception:
                pass

    def unhide_rows(self, iids: list[str] | None = None) -> None:
        """Restore previously hidden rows."""
        targets = iids or list(self._hidden_rows.keys())
        for iid in targets:
            if iid not in self._hidden_rows:
                continue
            parent, idx = self._hidden_rows.pop(iid)
            try:
                self._tree.move(iid, parent, idx)
            except Exception:
                pass
        self._apply_row_alternation()

    def hide_columns(self, indices: list[int]) -> None:
        """Remove columns from the displayed set."""
        for idx in indices:
            if idx in self._display_columns:
                self._display_columns.remove(idx)
        if not self._display_columns and self._heading_texts:
            self._display_columns = list(range(len(self._heading_texts)))
        self._tree.configure(displaycolumns=self._display_columns)

    def unhide_columns(self, indices: list[int]) -> None:
        """Add columns back into the displayed set."""
        changed = False
        for idx in indices:
            if idx not in self._display_columns and 0 <= idx < len(self._heading_texts):
                self._display_columns.append(idx)
                changed = True
        if changed:
            self._display_columns = sorted(self._display_columns)
            self._tree.configure(displaycolumns=self._display_columns)

    def select_rows(self, ids: list) -> None:
        """Select rows by record `id` (only those currently rendered)."""
        iids = [iid for iid in (self._iid_for_id(rid) for rid in ids) if iid]
        if iids:
            self._tree.selection_set(iids)

    def deselect_rows(self, ids: list | None = None) -> None:
        """Clear the selection, or remove specific rows by record `id`."""
        if not ids:
            self._tree.selection_remove(self._tree.selection())
            return
        iids = [iid for iid in (self._iid_for_id(rid) for rid in ids) if iid]
        if iids:
            self._tree.selection_remove(iids)

    def scroll_to_row(self, rid: Any) -> None:
        """Ensure the row with the given record `id` is visible."""
        iid = self._iid_for_id(rid)
        if iid is None:
            return
        try:
            self._tree.see(iid)
        except Exception:
            pass

    # ------------------------------------------------------------------ Pagination helpers
    def next_page(self) -> None:
        self._next_page()

    def previous_page(self) -> None:
        self._prev_page()

    def first_page(self) -> None:
        self._first_page()

    def last_page(self) -> None:
        self._last_page()

    def go_to_page(self, index: int) -> None:
        self._load_page(max(0, index))

    @property
    def current_page(self) -> int:
        """Zero-based index of the page currently shown."""
        return self._current_page

    @property
    def page_count(self) -> int:
        """Total number of pages for the current filter/search."""
        return self._total_pages()

    # ------------------------------------------------------------------ Filter/Sort/Group API
    def get_filters(self) -> dict[str, list]:
        """Return the active column filters as `{column_key: allowed_values}`."""
        return {k: list(v) for k, v in self._column_filters.items()}

    def clear_filters(self) -> None:
        """Remove all active column filters (leaves the search term intact)."""
        self._clear_filter_cmd()

    def set_filter(self, column: str, values=None) -> None:
        """Set a column filter (or clear it when `values` is None); composes with search."""
        if values is None:
            self._column_filters.pop(column, None)
        else:
            self._column_filters[column] = list(values)
        self._apply_where()

    def get_search(self) -> str:
        """Return the active free-text search term."""
        return self._search_text

    def set_search(self, text: str) -> None:
        """Set the free-text search term and re-apply (leaves column filters intact)."""
        text = text or ""
        entry = getattr(self, "_search_entry", None)
        if entry is not None:
            entry.delete(0, "end")
            entry.insert(0, text)
        self._search_text = text
        self._apply_where()

    def clear_search(self) -> None:
        """Clear the free-text search term (leaves column filters intact)."""
        self._clear_search()

    def get_sorting(self) -> dict[str, bool]:
        """Return a copy of the current sort state {column_key: ascending}."""
        return dict(self._sort_state)

    def set_sorting(self, key: str, ascending: bool = True) -> None:
        self._sort_state = {key: ascending}
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)
        self._update_status_labels()

    def clear_sorting(self) -> None:
        self._clear_sort()

    def get_grouping(self) -> str | None:
        return self._group_by_key

    def set_grouping(self, key: str | None) -> None:
        if not key:
            self._ungroup_all()
            return
        if key not in self._column_keys:
            return
        self._group_by_key = key
        self._group_parents.clear()
        self._sort_state = {key: True}
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)
        self._update_status_labels()

    def clear_grouping(self) -> None:
        self._ungroup_all()

    # ------------------------------------------------------------------ Group expand/collapse
    def expand_all(self) -> None:
        for iid in self._tree.get_children(""):
            try:
                self._tree.item(iid, open=True)
            except Exception:
                pass

    def collapse_all(self) -> None:
        for iid in self._tree.get_children(""):
            try:
                self._tree.item(iid, open=False)
            except Exception:
                pass

    def expand_group(self, group_value) -> None:
        parent = self._group_parents.get(group_value)
        if parent:
            try:
                self._tree.item(parent, open=True)
            except Exception:
                pass

    def collapse_group(self, group_value) -> None:
        parent = self._group_parents.get(group_value)
        if parent:
            try:
                self._tree.item(parent, open=False)
            except Exception:
                pass

    def select_all(self) -> None:
        """Select all visible rows."""
        self._tree.selection_set(self._tree.get_children(""))

    def deselect_all(self) -> None:
        """Clear the selection."""
        self._tree.selection_remove(self._tree.selection())

    # ------------------------------------------------------------------ UI

    def _resolve_alternating_row_color(self):
        from bootstack.style.utility import mix_colors

        style = get_style()
        builder = style.style_builder
        color_token = self._row_alternation.get('accent', 'background[+1]')

        try:
            stripe = builder.color(color_token)
            surface = builder.color('content')
            # Soften the stripe toward the table surface so it stays a faint
            # neutral that contrasts with the subtle accent selection.
            background = mix_colors(stripe, surface, _STRIPE_STRENGTH)
        except Exception:
            background = builder.color('background')

        try:
            foreground = builder.on_color(background)
        except Exception:
            foreground = builder.color('foreground')
        return background, foreground

    def _resolve_column_keys(self) -> None:
        if not self._column_defs:
            return
        for idx, col in enumerate(self._column_defs):
            if isinstance(col, str):
                self._column_keys.append(col)
            elif isinstance(col, dict):
                self._column_keys.append(col.get("key") or col.get("text") or str(idx))
            else:
                self._column_keys.append(str(col))

    def _ensure_column_metadata(self, sample_records: list[dict] | None) -> None:
        """Guarantee we have column keys/defs before the Treeview is built."""
        if self._column_keys:
            return

        inferred: list[str] = []
        if sample_records:
            first = sample_records[0]
            if isinstance(first, dict):
                inferred = list(first.keys())
        if not inferred:
            inferred = getattr(self._datasource, "_columns", []) or []

        _hidden = self._internal_fields()
        inferred = [c for c in inferred if c not in _hidden]
        if not inferred:
            inferred = ["value"]

        self._column_keys = inferred
        if not self._column_defs:
            self._column_defs = [{"text": c} for c in self._column_keys]

    def _build_toolbar(self) -> None:
        bar = Frame(self, name="toolbar")
        # Grid in column 0 only so the toolbar's right edge stops at the
        # tree's right edge instead of extending past the vsb.
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        if self._searchbar['enabled']:
            self._search_entry = TextEntry(bar, density=_CHROME_DENSITY)
            self._search_entry.insert_addon(Label, 'before', icon="search", icon_only=True)
            self._search_entry.insert_addon(Button, 'after', icon="x-lg", icon_only=True, command=self._clear_search)
            # Only reserve a 6 px right gap when the advanced-mode SelectBox
            # follows the entry; otherwise the entry hugs the toolbar edge.
            search_padx = (0, 6) if self._searchbar['mode'] == 'advanced' else 0
            self._search_entry.pack(side="left", fill="x", expand=True, padx=search_padx)
            trigger = str(self._searchbar.get('event', 'enter')).lower()
            if trigger == 'input':
                self._search_entry.on_input(lambda _e: self._run_search())
            else:
                self._search_entry.on_enter(lambda _e: self._run_search())
                # Clear filter when the box is emptied, but do not search on every keystroke
                self._search_entry.on_input(lambda _e: self._clear_search() if not self._search_entry.get() else None)

            if self._searchbar['mode'] == 'advanced':
                search_items = []
                self._search_mode_map = {}
                for token, code in _TABLE_SEARCH_MODE_OPTIONS:
                    label = MessageCatalog.translate(token)
                    search_items.append(label)
                    self._search_mode_map[label] = code
                default_value = search_items[0] if search_items else "EQUALS"
                self._search_mode = SelectBox(
                    bar,
                    items=search_items,
                    value=default_value,
                    width=14,
                    allow_custom_values=False,
                    enable_search=False,
                    density=_CHROME_DENSITY,
                )
                self._search_mode.pack(side="left", padx=(0, 6))

        if self._show_column_chooser:
            self._column_chooser_btn = Button(
                bar,
                icon="layout-three-columns",
                icon_only=True,
                accent="foreground",
                variant="ghost",
                density=_CHROME_DENSITY,
                command=self._show_column_chooser_dialog,
            )
            self._column_chooser_btn.pack(side="right", padx=(4, 0))

        if self._exporting['enabled']:
            export_items = [
                {"type": "command", "key": "export_copy", "text": "Copy to clipboard", "command": self._copy_to_clipboard},
                {"type": "command", "key": "export_save", "text": "Save to file", "command": self._save_to_file},
            ]
            self._export_btn = DropdownButton(
                bar,
                icon="download",
                icon_only=True,
                accent="foreground",
                variant="ghost",
                compound="image",
                density=_CHROME_DENSITY,
                items=export_items,
                show_dropdown_button=False,
            )
            self._export_btn.pack(side="right")

        if self._editing['adding']:
            Button(
                bar,
                icon="plus-circle",
                text="table.add_record",
                accent="foreground",
                variant="ghost",
                density=_CHROME_DENSITY,
                command=self._open_new_record,
            ).pack(side="right", padx=(0, 4))

    def _build_tree(self) -> None:
        cols = [self._col_text(c) for c in self._column_defs] or self._column_keys

        # Grid layout for the TableView body:
        #   row 0: toolbar     (col 0)
        #   row 1: tree        (col 0)   |   vsb (col 1, only this row)
        #   row 2: hsb         (col 0)
        #   row 3: footer      (col 0)
        # Column 0 expands; column 1 takes the vsb's natural width when present.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._tree = TreeView(
            self,
            columns=list(range(len(cols))),
            selectmode=_parse_selection_mode(self._selection['mode']),
            show="headings",
            density=self._density,
        )
        # Inset the tree by the focus-ring affordance baked into sibling
        # entry images so the tree's content edge lines up with the visible
        # edge of the toolbar/footer entries (search box, pagination input).
        from bootstack.style.style_builder_base import StyleBuilderBase
        affordance = StyleBuilderBase.scale_from_source(8)
        self._tree.grid(row=1, column=0, sticky="nsew", padx=affordance)
        self._display_columns = list(range(len(cols)))

        if self._paging['yscroll']:
            self._vsb = Scrollbar(self, orient="vertical", command=self._tree.yview)
            self._vsb.grid(row=1, column=1, sticky="ns")
            if self._paging['mode'] == "virtual":
                self._tree.configure(yscrollcommand=self._on_scroll)
            else:
                self._tree.configure(yscrollcommand=self._vsb.set)
        else:
            self._vsb = None

        if self._paging['xscroll']:
            self._hsb = Scrollbar(self, orient="horizontal", command=self._tree.xview)
            # Mirror the tree's affordance inset so the hsb aligns with the
            # tree content and stops at the same right edge.
            self._hsb.grid(row=2, column=0, sticky="ew", padx=affordance)
            self._tree.configure(xscrollcommand=self._hsb.set)
        else:
            self._hsb = None

        self._heading_texts = []
        self._column_anchors = []
        stretch_columns = not self._paging['xscroll']  # allow natural width when xscroll is enabled
        for idx, text in enumerate(cols):
            self._heading_texts.append(text)
            anchor = self._determine_anchor(idx)
            self._column_anchors.append(anchor)
            heading_kwargs = {"text": text, "anchor": anchor}
            # Don't use heading command - we'll handle clicks via Button-1 binding
            self._tree.heading(idx, **heading_kwargs)
            # Apply per-column width overrides, fall back to global defaults
            width = 120
            minwidth = self._column_min_width
            if idx < len(self._column_defs):
                coldef = self._column_defs[idx]
                if isinstance(coldef, dict):
                    width = coldef.get("width", width)
                    minwidth = coldef.get("minwidth", coldef.get("min_width", minwidth))
            self._tree.column(idx, anchor=anchor, width=width, minwidth=minwidth, stretch=stretch_columns)
        self._update_heading_icons()
        self._tree.bind("<Button-1>", self._on_header_click)
        self._tree.bind("<<TreeviewSelect>>", self._on_selection_event)
        # Keep group-header chevrons in sync with their open/closed state.
        self._tree.bind("<<TreeviewOpen>>", self._refresh_group_chevrons, add="+")
        self._tree.bind("<<TreeviewClose>>", self._refresh_group_chevrons, add="+")
        self._tree.bind("<ButtonRelease-1>", self._on_row_click_event)
        # Escape clears the selection (also reachable in single-select mode, where
        # clicking can't return to an empty selection). Bound on the tree widget
        # only (add='+'), so it fires solely when the tree has focus and never
        # clobbers dialog/menu/search Escape handling, which own their own focus.
        self._tree.bind("<Escape>", lambda _e: self.deselect_all(), add="+")
        if self._context_menus != "none":
            bind_right_click(self._tree, self._on_tree_context)
        if self._editing['updating']:
            self._tree.bind("<Double-1>", self._on_row_double_click)
        # Track resize events to rebalance grouped layouts
        self._tree.bind("<Configure>", self._on_tree_configure)

    def _build_footer(self) -> None:
        bar = Frame(self)
        # Same column 0 as the toolbar so the footer aligns with the table
        # content and stops at the vsb edge.
        bar.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        self._footer_bar = bar

        # A divider separating the footer from the table body. It lives inside
        # the footer bar, so it shows and hides together with the footer.
        self._footer_sep = Separator(bar, orient="horizontal")
        self._footer_sep.pack(side="top", fill="x", pady=(0, 6))

        status_frame = Frame(bar)
        status_frame.pack(side="left", fill="x", expand=True)
        self._filter_label = Label(status_frame, text="", anchor="w", accent="muted", font="caption")
        self._filter_label.pack(side="left", padx=(0, 4))
        self._sort_label = Label(status_frame, text="", anchor="w", accent="muted", font="caption")
        self._sort_label.pack(side="left", padx=(8, 4))

        # The pager (page entry + nav) is hidden when there is only one page.
        pager = Frame(bar)
        pager.pack(side="right")
        self._pager_frame = pager
        info_frame = Frame(pager)
        info_frame.pack(side='left')
        Label(info_frame, text="table.page", font="caption").pack(side='left')
        self._page_entry = Entry(info_frame, width=6, justify="center", density=_CHROME_DENSITY)
        self._page_entry.bind("<Return>", self._jump_page)
        self._page_entry.pack(side="left", padx=8)
        self._page_label = Label(info_frame, text="", font="caption")
        self._page_label.pack(side="left", padx=(0, 8))

        Separator(pager, orient="vertical").pack(side="left", fill="y", padx=8)

        btn_frame = Frame(pager)
        btn_frame.pack(side="left")
        Button(btn_frame, icon="chevron-double-left", accent="foreground", variant="ghost", icon_only=True, density=_CHROME_DENSITY, command=self._first_page).pack(
            side="left")
        Button(btn_frame, icon="chevron-left", icon_only=True, accent="foreground", variant="ghost", density=_CHROME_DENSITY, command=self._prev_page).pack(
            side="left")
        Button(btn_frame, icon="chevron-right", icon_only=True, accent="foreground", variant="ghost", density=_CHROME_DENSITY, command=self._next_page).pack(
            side="left")
        Button(btn_frame, icon="chevron-double-right", icon_only=True, accent="foreground", variant="ghost", density=_CHROME_DENSITY, command=self._last_page).pack(
            side="left")

        self._update_footer_visibility()

    def _update_footer_visibility(self) -> None:
        """Hide the pager on a single page and collapse the footer when empty.

        `show_status_bar=False` hides the whole footer.
        """
        bar = getattr(self, "_footer_bar", None)
        if bar is None:
            return
        if not self._show_table_status:
            bar.grid_remove()
            return
        multipage = self._total_pages() > 1
        has_status = bool(self._filter_label.cget("text")) or bool(self._sort_label.cget("text"))
        if multipage:
            if not self._pager_frame.winfo_manager():
                self._pager_frame.pack(side="right")
        else:
            self._pager_frame.pack_forget()
        if multipage or has_status:
            bar.grid()
        else:
            bar.grid_remove()

    # ------------------------------------------------------------------ Helpers
    def _col_text(self, col) -> str:
        if isinstance(col, str):
            return col
        if isinstance(col, dict):
            return col.get("text") or col.get("key") or ""
        return str(col)

    def _header_context_enabled(self) -> bool:
        return self._context_menus in ("all", "headers")

    def _row_context_enabled(self) -> bool:
        return self._context_menus in ("all", "rows")

    def _determine_anchor(self, idx: int) -> str:
        """Pick an anchor for the given column index.

        Priority:
            1) Explicit anchor/align in column definition
            2) Explicit dtype/type hint in column definition (numeric -> right)
            3) Numeric columns -> right
            4) Default -> left
        """
        if idx < len(self._column_defs):
            coldef = self._column_defs[idx]
            if isinstance(coldef, dict):
                anchor = coldef.get("anchor") or coldef.get("align")
                if anchor:
                    return anchor
                # Allow a dtype/type hint on the column definition
                dtype = coldef.get("dtype") or coldef.get("type")
                if dtype:
                    dtype_upper = str(dtype).upper()
                    if any(t in dtype_upper for t in ("INT", "REAL", "NUM", "DECIMAL", "DOUBLE", "FLOAT")):
                        return "e"
                    if "TEXT" in dtype_upper or "STR" in dtype_upper or "CHAR" in dtype_upper:
                        return "w"
        # Infer from type
        key = self._column_keys[idx] if idx < len(self._column_keys) else None
        ctype = self._get_column_type(key) if key else ""
        if ctype and any(t in ctype.upper() for t in ("INT", "REAL", "NUM", "DECIMAL", "DOUBLE", "FLOAT")):
            return "e"
        # Fallback: sample values to detect numeric strings
        if self._is_numeric_sample(idx):
            return "e"
        return "w"

    def _get_column_type(self, key: str | None) -> str:
        if not key:
            return ""
        if key in self._column_types:
            return self._column_types[key]
        # Try PRAGMA table_info
        try:
            cur = self._datasource.conn.execute(f"PRAGMA table_info({self._datasource._table})")
            for cid, name, ctype, *_rest in cur.fetchall():
                if name == key:
                    self._column_types[key] = ctype or ""
                    return self._column_types[key]
        except Exception:
            pass
        return ""

    def _load_alignment_sample(self) -> list[dict]:
        if self._alignment_sample is not None:
            return self._alignment_sample
        try:
            sample = self._datasource.page(0)
        except Exception:
            sample = []
        self._alignment_sample = sample or []
        return self._alignment_sample

    def _is_numeric_sample(self, idx: int) -> bool:
        """Check sample values to decide if a column with text storage is numeric-like."""
        key = self._column_keys[idx] if idx < len(self._column_keys) else None
        if not key:
            return False
        sample = self._load_alignment_sample()
        if not sample:
            return False

        def is_num(val) -> bool:
            if val is None or val == "":
                return True
            try:
                float(val)
                return True
            except Exception:
                return False

        seen = 0
        for rec in sample[: min(20, len(sample))]:
            if key not in rec:
                continue
            seen += 1
            if not is_num(rec.get(key)):
                return False
        return seen > 0

    def _to_records(self, rows: list) -> list[dict]:
        records: list[dict] = []
        if not rows:
            return records
        keys = self._column_keys or [str(i) for i in range(len(rows[0]))]
        for rec in rows:
            if isinstance(rec, dict):
                records.append(rec)
            else:
                records.append({k: rec[i] if i < len(rec) else "" for i, k in enumerate(keys)})
        return records

    def _refresh_tree(self, records: list[dict]) -> None:
        # Preserve the selection across the rebuild for rows that remain visible.
        # Selection is view/page-scoped: a sort keeps every row (selection fully
        # preserved), a search keeps the still-matching rows, and rows no longer
        # shown drop out. Captured by record id since the row handles are rebuilt.
        prev_selected_ids = {
            self._record_id(self._row_map[iid])
            for iid in self._tree.selection() if iid in self._row_map
        }
        self._tree.delete(*self._tree.get_children())
        self._row_map.clear()
        if not self._column_keys and records:
            self._column_keys = list(records[0].keys())
        grouped = bool(self._group_by_key) and self._group_by_key in self._column_keys
        self._apply_group_show_state(grouped)
        if grouped:
            self._render_grouped(records)
        else:
            self._render_flat(records)
        self._apply_row_alternation()
        if prev_selected_ids:
            restore = [iid for iid, rec in self._row_map.items()
                       if self._record_id(rec) in prev_selected_ids]
            if restore:
                self._tree.selection_set(restore)
        self._update_selection_markers()

    def _append_tree(self, records: list[dict]) -> None:
        # Grouped mode rebuilds the view instead of appending to keep hierarchy consistent
        if self._group_by_key:
            self._refresh_tree(records)
            return
        stripe = self._row_alternation.get('enabled', False) and not self._group_by_key
        start_idx = len(self._tree.get_children(""))
        for offset, rec in enumerate(records):
            values = self._display_values(rec)
            tags = ("altrow",) if stripe and (start_idx + offset) % 2 == 1 else ()
            iid = self._tree.insert("", "end", values=values, tags=tags)
            self._row_map[iid] = rec
        self._apply_row_alternation()
        self._update_selection_markers()

    def _total_pages(self) -> int:
        try:
            if self._cached_total_count is None:
                with self._apply_view_to_source():
                    self._cached_total_count = self._datasource.count
            total = self._cached_total_count
            size = getattr(self._datasource, "page_size", self._paging['page_size']) or 1
            return max(1, (total + size - 1) // size)
        except Exception:
            return 1

    # ------------------------------------------------------------------ Paging
    def _load_page(self, page: int, append: bool = False) -> None:
        if not append and page in self._page_cache:
            records = self._page_cache[page]
        else:
            with self._apply_view_to_source():
                try:
                    records = self._datasource.page(page)
                    if self._cached_total_count is None:
                        self._cached_total_count = self._datasource.count
                except Exception:
                    records = []
            if not append:
                self._remember_page(page, records)
        self._current_page = max(0, page)
        try:
            if append:
                self._append_tree(records)
            else:
                self._refresh_tree(records)
            if self._column_auto_width:
                self._auto_size_columns(records if not append else None)
            self._update_page_label()
        finally:
            self._loading_next = False

    def _update_page_label(self) -> None:
        if hasattr(self, "_page_entry"):
            self._page_entry.delete(0, 'end')
            self._page_entry.insert(0, str(self._current_page + 1))
        if hasattr(self, "_page_label"):
            of_text = MessageCatalog.translate("table.of")
            self._page_label.configure(text=f"{of_text} {self._total_pages()}")
        if self._show_table_status:
            self._update_status_labels()

    def _first_page(self) -> None:
        self._load_page(0)

    def _prev_page(self) -> None:
        self._load_page(max(0, self._current_page - 1))

    def _next_page(self) -> None:
        self._load_page(min(self._total_pages() - 1, self._current_page + 1))

    def _last_page(self) -> None:
        self._load_page(self._total_pages() - 1)

    def _jump_page(self, _event=None) -> None:
        try:
            target = int(self._page_entry.get()) - 1
        except Exception:
            return
        target = max(0, min(self._total_pages() - 1, target))
        self._load_page(target)

    def _on_scroll(self, first: float, last: float) -> None:
        """Drive scrollbar and trigger lazy loading when near the bottom."""
        # Grouped mode disables virtual scroll append to avoid breaking hierarchy
        if self._group_by_key:
            self._vsb.set(first, last)
            return
        try:
            first_f = float(first)
            last_f = float(last)
        except Exception:
            self._vsb.set(first, last)
            return

        self._vsb.set(first_f, last_f)
        if (
                self._paging['mode'] == "virtual"
                and last_f >= 0.85  # prefetch a bit earlier for smoother scrolling
                and not self._loading_next
                and hasattr(self._datasource, "has_next_page")
                and self._datasource.has_next_page()
        ):
            # Load next page and keep appending rows
            self._loading_next = True
            self._load_page(self._current_page + 1, append=True)

    # ------------------------------------------------------------------ Search & sort
    def _build_search_condition(self):
        """Build the search condition from the active search term (or None)."""
        text = self._search_text
        if not text or not self._column_keys:
            return None
        if hasattr(self, "_search_mode") and self._search_mode_map:
            display_mode = self._search_mode.get()
            mode = self._search_mode_map.get(display_mode, "CONTAINS")
        else:
            mode = "CONTAINS"
        mode_upper = mode.upper().replace(" ", "_")
        if mode_upper == "STARTS_WITH":
            make = lambda c: col(c).startswith(text)
        elif mode_upper == "ENDS_WITH":
            make = lambda c: col(c).endswith(text)
        elif mode_upper == "EQUALS":
            make = lambda c: col(c) == text
        else:  # CONTAINS (default)
            make = lambda c: col(c).contains(text)
        return any_of(*(make(c) for c in self._column_keys))

    def _apply_where(self) -> None:
        """Recompute and apply the table's local filter state.

        When `broadcast_search` is enabled, the combined condition is written to
        the source un-silenced so that all other views (charts, etc.) re-render.
        The table suppresses its own `_on_source_change` callback for this write
        to avoid a double page-load.
        """
        if self._broadcast_search:
            condition = all_of(
                self._build_search_condition(),
                self._build_column_filter_condition(),
            )
            try:
                # Set the flag BEFORE the write; clear it in _on_source_change
                # (not here in finally) so it is still True when the hub's
                # after_idle flush fires, preventing a redundant second reload.
                self._suppressing_search_broadcast = True
                self._datasource.where(condition)
            except Exception:
                logger.exception("Failed to broadcast search filter")
                self._suppressing_search_broadcast = False  # clear on error
        self._clear_cache()
        self._load_page(0)
        self._update_status_labels()

    def _run_search(self) -> None:
        self._search_text = self._search_entry.get()
        self._apply_where()

    def _clear_search(self) -> None:
        entry = getattr(self, "_search_entry", None)
        if entry is not None:
            entry.delete(0, 'end')
        self._search_text = ""
        self._apply_where()

    def _on_sort(self, column_index: int) -> None:
        if column_index >= len(self._column_keys):
            return
        key = self._column_keys[column_index]
        asc = not self._sort_state.get(key, True)
        # Clear other sort states to keep single-column sort
        self._sort_state = {key: asc}
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)
        self._update_status_labels()

    def _column_heading(self, key: str) -> str:
        """Display heading for a column key (falls back to the key)."""
        try:
            idx = self._column_keys.index(key)
            return self._heading_texts[idx] if idx < len(self._heading_texts) else key
        except Exception:
            return key

    def _filter_description(self) -> str:
        """Human-readable summary of the active search term and column filters.

        The search term spans all columns (`'term' in any column`); each column
        filter reads like `Heading='value'` (or `Heading in (...)` for several).
        """
        def fmt(v) -> str:
            return "(blank)" if v is None else f"'{v}'"

        parts = []
        if self._search_text:
            parts.append(f"{fmt(self._search_text)} in any column")
        for key, values in self._column_filters.items():
            heading = self._column_heading(key)
            vals = list(values)
            if len(vals) == 1:
                parts.append(f"{heading}={fmt(vals[0])}")
            else:
                parts.append(f"{heading} in ({', '.join(fmt(v) for v in vals)})")
        return ", ".join(parts)

    def _update_filter_tooltip(self, text: str) -> None:
        """Show a hover tooltip with the full filter text, or remove it."""
        if not hasattr(self, "_filter_label"):
            return
        if text:
            if self._filter_tooltip is None:
                self._filter_tooltip = ToolTip(self._filter_label, text=text)
            else:
                self._filter_tooltip._text = text
        elif self._filter_tooltip is not None:
            self._filter_tooltip.destroy()
            self._filter_tooltip = None

    def _update_status_labels(self) -> None:
        # Filter — summarize the active search term and any column filters,
        # truncating the label and revealing the full text via tooltip on overflow.
        filter_txt = ""
        tooltip_txt = ""
        try:
            description = self._filter_description()
            if description:
                shown = description
                if len(description) > _FILTER_STATUS_MAXLEN:
                    shown = description[: _FILTER_STATUS_MAXLEN - 1].rstrip() + "…"
                filter_txt = MessageCatalog.translate("table.filter_status", shown)
                if shown != description:
                    tooltip_txt = MessageCatalog.translate("table.filter_status", description)
        except Exception:
            pass
        self._update_filter_tooltip(tooltip_txt)
        # Sort
        sort_txt = ""
        try:
            if self._sort_state and not self._group_by_key:
                key, ascending = next(iter(self._sort_state.items()))
                heading = self._column_heading(key)
                direction = "↑" if ascending else "↓"
                sort_txt = MessageCatalog.translate("table.sort_status", f"{heading} {direction}")
        except Exception:
            pass
        group_txt = ""
        if self._group_by_key:
            try:
                col_idx = self._column_keys.index(self._group_by_key)
                heading_text = self._heading_texts[col_idx] if col_idx < len(
                    self._heading_texts) else self._group_by_key
            except Exception:
                heading_text = self._group_by_key
            group_txt = MessageCatalog.translate("table.group_status", heading_text)

        if hasattr(self, "_filter_label"):
            self._filter_label.configure(text=filter_txt)
        if hasattr(self, "_sort_label"):
            joined = " | ".join([t for t in (sort_txt, group_txt) if t])
            self._sort_label.configure(text=joined)
        self._update_footer_visibility()

    # ------------------------------------------------------------------ Row context menu
    def _dismiss_context_menus(self) -> None:
        """Hide any open built-in row/header context menu (idempotent)."""
        for menu in (self._row_menu, self._header_menu):
            if menu is not None:
                try:
                    menu.hide()
                except Exception:
                    pass

    def _ensure_row_menu(self) -> None:
        if not self._row_context_enabled():
            return
        if self._row_menu:
            return
        # Activation is wired upstream by bind_right_click on the tree so the
        # row vs header dispatch can run before the (lazily built) menu
        # decides which one to show.
        menu = ContextMenu(master=self, target=self._tree, attach='sw', trigger=None)
        if not self._sorting == 'none':
            menu.add_command(text="table.sort_asc", command=lambda: self._sort_selection(True))
            menu.add_command(text="table.sort_desc", command=lambda: self._sort_selection(False))

        if self._filtering['row_menu_filtering']:
            menu.add_separator()
            menu.add_command(text="table.filter_by_value", command=self._filter_by_value)
            menu.add_command(text="table.hide_select", command=self._hide_selection)
            menu.add_command(text="table.clear_filters", command=self._clear_filter_cmd)

        menu.add_separator()
        menu.add_command(text="table.move_up", command=self._move_row_up)
        menu.add_command(text="table.move_down", command=self._move_row_down)
        menu.add_command(text="table.move_top", command=self._move_row_top)
        menu.add_command(text="table.move_bottom", command=self._move_row_bottom)

        if self._editing['updating'] or self._editing['deleting']:
            menu.add_separator()
            if self._editing['updating']:
                menu.add_command(text="table.edit", command=self._edit_selected_row)
            if self._editing['deleting']:
                menu.add_command(text="table.delete_row", command=self._delete_selected_row)
        self._row_menu = menu

    def _on_row_context(self, event) -> None:
        if not self._row_context_enabled():
            return
        iid = self._tree.identify_row(event.y)
        col_id = self._tree.identify_column(event.x)
        try:
            col_idx = int(col_id.strip("#")) - 1
        except Exception:
            col_idx = 0
        # Right-click does not alter the selection (left-click owns that); it
        # only records which row the menu targets and opens the menu there.
        self._context_iid = iid or None
        if not iid:
            return  # empty space or a group-header row — no row menu
        rec = self._row_map.get(iid, {})
        self.event_generate("<<RowRightClick>>", data=RowEvent(record=self._public_record(rec), id=self._record_id(rec)))
        self._row_menu_col = col_idx
        self._ensure_row_menu()
        self._row_menu.show(position=(event.x_root, event.y_root))

    def _on_row_double_click(self, event) -> None:
        region = self._tree.identify_region(event.x, event.y)
        if region == "heading":
            return
        iid = self._tree.identify_row(event.y)
        if not iid:
            return
        rec = self._row_map.get(iid, {})
        self.event_generate("<<RowDoubleClick>>", data=RowEvent(record=self._public_record(rec), id=self._record_id(rec)))
        if self._editing['updating']:
            self._open_form_dialog(rec)

    def _open_new_record(self) -> None:
        if not self._editing['adding']:
            return
        self._open_form_dialog(None)

    def new_row(self, defaults: dict | None = None) -> dict | None:
        """Open the built-in New Record dialog; return the new record or None."""
        return self._open_form_dialog(None, defaults=defaults)

    def edit_row(self, record_id) -> dict | None:
        """Open the built-in Edit Record dialog for `record_id`; return it or None."""
        record = self._datasource.get(record_id)
        if record is None:
            return None
        return self._open_form_dialog(record)

    def _open_form_dialog(self, record: dict | None, *, defaults: dict | None = None) -> dict | None:
        from bootstack.dialogs._impl.formdialog import FormDialog

        try:
            # Ensure geometry info is current so centering uses real widget bounds
            self.update_idletasks()
        except Exception:
            pass
        dialog_master = self.winfo_toplevel() if hasattr(self, "winfo_toplevel") else self

        form_items = self._build_form_items()
        initial_data = dict(record) if record else dict(defaults or {})

        form_options = dict(self._editing['form'])
        form_options.setdefault('col_count', 2)
        form_options.setdefault('min_col_width', 260)
        form_options.setdefault('scrollable', True)
        form_options.setdefault('resizable', True)

        # Build buttons: Cancel, Delete (only for existing records), Save
        record_id = self._record_id(record)
        if record and record_id is not None:
            buttons: list[str | dict] = ['Cancel']
            if self._editing['deleting']:
                buttons.append({"text": "Delete", "role": "secondary", "result": "delete"})
            buttons.append("Save")
        else:
            buttons = ["Cancel", "Save"]

        dialog = FormDialog(
            parent=dialog_master,
            title="Edit Record" if record else "New Record",
            data=initial_data,
            items=form_items,
            col_count=form_options.get('col_count', 2),
            min_col_width=form_options.get('min_col_width', 260),
            scrollable=form_options.get('scrollable', True),
            buttons=buttons,
            resizable=(True, True) if form_options.get('resizable', True) else (False, False),
        )

        self._active_form_dialog = dialog
        try:
            dialog.show()   # centers over the parent window (the table)
        finally:
            self._active_form_dialog = None
        result = dialog.result

        if result is None:
            return None

        # Handle delete action
        if result == "delete" and record and record_id is not None:
            deleted = self._public_record(record)
            try:
                with self._silence_source():
                    self._datasource.delete(record_id)
                self._clear_cache()
                self._load_page(self._current_page)
                self.event_generate("<<RowsDelete>>", data=RowsEvent(records=[deleted]))
            except Exception:
                logger.exception("Failed to delete record id=%s", record_id)
            return None

        data = result
        new_id = None
        if record and record_id is not None:
            rec_id = record_id
            updates = dict(data)
            for _f in self._internal_fields():
                updates.pop(_f, None)
            try:
                with self._silence_source():
                    self._datasource.update(rec_id, updates)
            except Exception:
                logger.exception("Failed to update record id=%s", rec_id)
                return None
            saved_id, change_event = rec_id, "<<RowsUpdate>>"
        else:
            try:
                with self._silence_source():
                    new_id = self._datasource.insert(dict(data))
            except Exception:
                logger.exception("Failed to create record from %s", data)
                return None
            saved_id, change_event = new_id, "<<RowsInsert>>"
        self._clear_cache()
        target_page = self._current_page
        if not record:
            # After creating, compute last page using fresh count so the new row is visible
            located_page = self._find_record_page(new_id) if new_id is not None else None
            target_page = located_page if located_page is not None else max(0, self._total_pages() - 1)
        self._load_page(target_page)
        if new_id is not None:
            self._focus_record(new_id)
        saved = None
        if saved_id is not None:
            fresh = self._datasource.get(saved_id)
            if fresh is not None:
                saved = self._public_record(fresh)
        if saved is not None:
            self.event_generate(change_event, data=RowsEvent(records=[saved]))
        return saved

    def _build_form_items(self) -> list[dict]:
        items: list[dict] = []
        for idx, key in enumerate(self._column_keys):
            coldef = self._column_defs[idx] if idx < len(self._column_defs) else key
            label = self._col_text(coldef)
            editor_opts = {}
            editor = None
            dtype = None
            readonly = False
            if isinstance(coldef, dict):
                editor_opts = dict(coldef.get("editor_options", {}))
                editor = coldef.get("editor")
                dtype = coldef.get("dtype") or coldef.get("type")
                readonly = bool(coldef.get("readonly", False))
                if coldef.get("required"):
                    editor_opts.setdefault("required", True)
            # Show validation messages to avoid layout jump on first error
            editor_opts.setdefault("show_message", True)
            items.append(
                {
                    "key": key,
                    "label": label,
                    "dtype": dtype,
                    "editor": editor,
                    "editor_options": {**editor_opts},
                    "readonly": readonly,
                    "type": "field",
                }
            )
        return items

    def _context_iids(self) -> tuple[str, ...]:
        """Row id(s) a row-menu command acts on.

        The menu targets the right-clicked row. When that row is part of the
        current (left-click) selection, the whole selection is the target — the
        intuitive multi-select behavior — otherwise just the clicked row. Either
        way the selection itself is left unchanged.
        """
        clicked = self._context_iid
        selection = tuple(self._tree.selection())
        if clicked and clicked in selection:
            return selection
        if clicked:
            return (clicked,)
        return selection

    def _filter_by_value(self) -> None:
        selection = self._context_iids()
        if not selection:
            return
        iid = selection[0]
        col_idx = max(0, min(self._row_menu_col or 0, len(self._column_keys) - 1))
        key = self._column_keys[col_idx]
        rec = self._row_map.get(iid)
        if rec is None:
            return
        # Use the stored record value (real type, handles None) rather than the
        # Tk display string, so the filter and status read correctly.
        self._column_filters[key] = [rec.get(key)]
        self._apply_where()

    def _sort_selection(self, ascending: bool) -> None:
        selection = self._context_iids()
        if not selection:
            return
        iid = selection[0]
        col_idx = max(0, min(self._row_menu_col or 0, len(self._column_keys) - 1))
        key = self._column_keys[col_idx]
        self._sort_state = {key: ascending}
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)

    def _clear_filter_cmd(self) -> None:
        self._column_filters.clear()
        self._apply_where()

    def _move_row_up(self) -> None:
        self._move_row_relative(-1)

    def _move_row_down(self) -> None:
        self._move_row_relative(1)

    def _move_row_top(self) -> None:
        self._move_row_absolute(0)

    def _move_row_bottom(self) -> None:
        children = list(self._tree.get_children())
        if children:
            self._move_row_absolute(len(children) - 1)

    def _move_row_relative(self, delta: int) -> None:
        sel = list(self._context_iids())
        if not sel:
            return
        target_iid = sel[0]
        children = list(self._tree.get_children())
        try:
            idx = children.index(target_iid)
        except ValueError:
            return
        new_idx = max(0, min(len(children) - 1, idx + delta))
        if new_idx == idx:
            return
        self._tree.move(target_iid, "", new_idx)
        self._apply_row_alternation()
        rec = self._row_map.get(target_iid)
        if rec:
            self.event_generate("<<RowsMove>>", data=RowsEvent(records=[self._public_record(rec)]))

    def _move_row_absolute(self, new_idx: int) -> None:
        sel = list(self._context_iids())
        if not sel:
            return
        target_iid = sel[0]
        children = list(self._tree.get_children())
        new_idx = max(0, min(len(children) - 1, new_idx))
        self._tree.move(target_iid, "", new_idx)
        self._apply_row_alternation()
        rec = self._row_map.get(target_iid)
        if rec:
            self.event_generate("<<RowsMove>>", data=RowsEvent(records=[self._public_record(rec)]))

    def _hide_selection(self) -> None:
        sel = list(self._context_iids())
        for iid in sel:
            self._tree.delete(iid)
            self._row_map.pop(iid, None)

    def _edit_selected_row(self) -> None:
        """Open the form dialog for the right-clicked row."""
        sel = list(self._context_iids())
        if not sel:
            return
        iid = sel[0]
        rec = self._row_map.get(iid, {})
        self._open_form_dialog(rec)

    def _delete_selected_row(self) -> None:
        """Delete the right-clicked row from the datasource."""
        sel = list(self._context_iids())
        if not sel:
            return
        iid = sel[0]
        rec = self._row_map.get(iid, {})
        rec_id = self._record_id(rec)
        if rec_id is not None:
            try:
                with self._silence_source():
                    self._datasource.delete(rec_id)
                self._clear_cache()
                self._load_page(self._current_page)
                self.event_generate("<<RowsDelete>>", data=RowsEvent(records=[self._public_record(rec)]))
            except Exception:
                logger.exception("Failed to delete record id=%s", rec_id)

    def _delete_selection(self) -> None:
        sel = list(self._tree.selection())
        deleted_records: list[dict] = []
        changed = False
        with self._silence_source():
            for iid in sel:
                rec = dict(self._row_map.get(iid) or {})
                if rec:
                    deleted_records.append(rec)
                rec_id = self._record_id(rec)
                if rec_id is not None:
                    try:
                        self._datasource.delete(rec_id)
                        changed = True
                    except Exception:
                        pass
                self._row_map.pop(iid, None)
        if changed:
            self._clear_cache()
            self._load_page(self._current_page)
            if deleted_records:
                records = [self._public_record(r) for r in deleted_records]
                self.event_generate("<<RowsDelete>>", data=RowsEvent(records=records))

    # ------------------------------------------------------------------ Cache helpers
    def _clear_cache(self) -> None:
        if self._page_cache:
            self._page_cache.clear()
        # Invalidate total count cache when data/filter/sort changes
        self._cached_total_count = None

    def _load_heading_icons(self) -> None:
        """Load and cache heading icons (sort arrows) sized to match the heading color."""
        try:
            fg = self._get_heading_fg()
            if fg == self._heading_fg and self._icon_sort_up:
                return
            self._heading_fg = fg
            self._icon_sort_up = _ImageService.get_icon("sort-up", 16, fg)
            self._icon_sort_down = _ImageService.get_icon("sort-down", 16, fg)
        except Exception:
            self._icon_sort_up = None
            self._icon_sort_down = None

    def _get_heading_fg(self) -> str:
        """Resolve a heading foreground color with light-biased fallbacks."""
        style = get_style()
        ttk_style = self._tree.cget('style')
        # Try configured value first
        return style.configure(f"{ttk_style}.Heading", 'foreground')

    def _update_heading_icons(self) -> None:
        """Apply sort direction icons to headings."""
        if not self._heading_texts:
            return
        self._load_heading_icons()
        for idx, text in enumerate(self._heading_texts):
            image = ""
            if idx < len(self._column_keys):
                key = self._column_keys[idx]
                state = self._sort_state.get(key)
                if state is True:
                    image = self._icon_sort_up if self._icon_sort_up else ""
                elif state is False:
                    image = self._icon_sort_down if self._icon_sort_down else ""
            self._tree.heading(idx, text=text, image=image)

    def _remember_page(self, page: int, records: list[dict]) -> None:
        if self._paging['cache_size'] <= 0:
            return
        # Move/update LRU cache
        if page in self._page_cache:
            self._page_cache.pop(page)
        self._page_cache[page] = records
        if len(self._page_cache) > self._paging['cache_size']:
            self._page_cache.popitem(last=False)

    def _focus_record(self, record_id) -> None:
        """Select and scroll to a record by id if it's on the current page."""
        try:
            rid = str(record_id)
            for iid, rec in self._row_map.items():
                if str(self._record_id(rec)) == rid:
                    self._tree.selection_set(iid)
                    self._tree.see(iid)
                    break
        except Exception:
            pass

    def _find_record_page(self, record_id) -> int | None:
        """Locate the page index containing the given record id, if available."""
        try:
            rid = str(record_id)
            total_pages = self._total_pages()
            for page_idx in range(total_pages):
                try:
                    with self._apply_view_to_source():
                        rows = self._datasource.page(page_idx)
                except Exception:
                    break
                if any(str(self._record_id(rec)) == rid for rec in rows):
                    return page_idx
        except Exception:
            pass
        return None

    def _auto_size_columns(self, records: list[dict] | None = None) -> None:
        """Auto-size columns to the widest value among current rows/headings."""
        if not self._column_keys:
            return
        try:
            style = get_style()
            # Prefer the Treeview body font; fall back to TLabel/body or default
            tv_style = self._tree.cget("style") or "Treeview"
            body_font = (
                    style.lookup(tv_style, "font")
                    or style.lookup("TLabel", "font")
                    or getattr(style, "fonts", {}).get("body")
                    or "TkDefaultFont"
            )
            content_font = tkfont.nametofont(body_font)
        except Exception:
            content_font = None

        pad_px = 20

        # Gather samples from headings, provided records, and current tree values
        tree_samples = []
        for iid in self._tree.get_children(""):
            tree_samples.append(self._tree.item(iid, "values"))
            for ciid in self._tree.get_children(iid):
                tree_samples.append(self._tree.item(ciid, "values"))

        for idx, key in enumerate(self._column_keys):
            samples = []
            if idx < len(self._heading_texts):
                samples.append(str(self._heading_texts[idx]))
            if records:
                for rec in records:
                    samples.append(str(rec.get(key, "")))
            for vals in tree_samples:
                if idx < len(vals):
                    samples.append(str(vals[idx]))

            # Honor explicit column width if provided
            explicit_width = None
            if idx < len(self._column_defs):
                coldef = self._column_defs[idx]
                if isinstance(coldef, dict):
                    explicit_width = coldef.get("width")

            if explicit_width is not None:
                try:
                    self._tree.column(idx, width=explicit_width, minwidth=self._column_min_width)
                except Exception:
                    pass
                continue

            text = max(samples, key=len) if samples else ""
            if content_font:
                width = content_font.measure(text) + pad_px
            else:
                width = 0
            # Fallback to simple char-based estimate to avoid under-measuring
            char_estimate = len(text) * 10 + pad_px
            width = max(width, char_estimate, self._column_min_width)
            # Cap width to available viewport so we don't force the tree wider than its frame
            try:
                avail = max(0, int(self._tree.winfo_width()) - pad_px)
                if avail > 0:
                    width = min(width, avail)
            except Exception:
                pass
            try:
                self._tree.column(idx, width=width, minwidth=self._column_min_width)
            except Exception:
                pass

    def _on_theme_changed(self, _event: Any = None) -> None:
        """Re-resolve the imperative stripe tag colors on a theme change (tag
        colors aren't refreshed by the ttk style rebuild)."""
        try:
            self._apply_row_alternation()
        except Exception:
            pass

    def _apply_row_alternation(self) -> None:
        """Apply alternating row colors via a tag."""
        enabled = self._row_alternation.get('enabled', False)
        if not enabled or self._group_by_key:
            return
        bg, fg = self._resolve_alternating_row_color()
        try:
            self._tree.tag_configure("altrow", background=bg, foreground=fg)
            # Some themes honor the "striped" tag name; configure it too
            self._tree.tag_configure("striped", background=bg, foreground=fg)
        except Exception:
            return

        queue = list(self._tree.get_children(""))
        idx = 0
        while queue:
            iid = queue.pop(0)
            try:
                tags = list(self._tree.item(iid, "tags") or [])
                if idx % 2 == 1:
                    if "altrow" not in tags:
                        tags.append("altrow")
                    if "striped" not in tags:
                        tags.append("striped")
                else:
                    tags = [t for t in tags if t not in ("altrow", "striped")]
                self._tree.item(iid, tags=tags)
            except Exception:
                pass
            queue.extend(list(self._tree.get_children(iid)))
            idx += 1

    # ------------------------------------------------------------------ Selection markers
    def _selection_markers_active(self) -> bool:
        """Whether per-row selection checkboxes should be shown right now.

        Multi-select only — single-select relies on the row highlight alone, and
        grouped mode reserves the leading slot for the expand/collapse control.
        """
        return (
            self._selection_indicators
            and not self._group_by_key
            and self._selection.get('mode', 'single') == 'multi'
        )

    def _marker_icon_specs(self) -> tuple[int, str]:
        """Resolve (size, color) for marker icons from the active theme.

        Rendered at a fixed even pixel size: the glyph is blitted 1:1 into the
        row, so a clean target size keeps it crisp and avoids the resampling
        softness that DPI-scaling a small icon introduces.
        """
        builder = get_style().style_builder
        try:
            color = builder.on_color(builder.color('content'))
        except Exception:
            color = '#000000'
        return _MARKER_ICON_SIZE, color

    def _marker_column_width(self) -> int:
        """Width for the tree column (#0) when it hosts a selection marker.

        Accounts for the icon plus the indicator/spacer/padding the shared item
        layout reserves ahead of the image slot.
        """
        size, _ = self._marker_icon_specs()
        try:
            pad = get_style().style_builder.scale(24)
        except Exception:
            pad = 24
        return int(size + pad)

    def _marker_accent_color(self) -> str:
        """Solid accent color used to fill the checked/selected marker glyph."""
        builder = get_style().style_builder
        token = self._selection.get('accent', 'primary')
        try:
            return builder.color(token)
        except Exception:
            try:
                return builder.color('primary')
            except Exception:
                return self._marker_icon_specs()[1]

    def _marker_unchecked_color(self) -> str:
        """Color for the empty (unchecked) box outline — a muted neutral."""
        builder = get_style().style_builder
        try:
            return builder.color('muted')
        except Exception:
            return self._marker_icon_specs()[1]

    def _marker_icon(self, name: str | None, color: str | None = None):
        """Return a cached marker icon for the current theme.

        `color` overrides the default neutral foreground (used to fill the
        checked/selected glyph with the accent). A `name` of None yields a
        transparent placeholder so unmarked rows keep their text alignment.
        """
        size, default_color = self._marker_icon_specs()
        use_color = color or default_color
        key = (name, size, use_color)
        cached = self._marker_icons.get(key)
        if cached is not None:
            return cached
        try:
            if name is None:
                from bootstack.style.utility import create_transparent_image
                img = create_transparent_image(size, size)
            else:
                img = _ImageService.get_icon(name, size, use_color)
        except Exception:
            return None
        self._marker_icons[key] = img
        return img

    def _update_selection_markers(self) -> None:
        """Mirror the current selection as a per-row checkbox (multi-select).

        Visual only — selection is still driven by clicks/keyboard. The checked
        box is filled with the accent; the unchecked box is a muted outline.
        """
        if not self._selection_markers_active():
            return
        selected = set(self._tree.selection())
        on_icon = self._marker_icon('check-square-fill', self._marker_accent_color())
        off_icon = self._marker_icon('square', self._marker_unchecked_color())
        for iid in self._tree.get_children(""):
            img = on_icon if iid in selected else off_icon
            try:
                self._tree.item(iid, image=img if img is not None else "")
            except Exception:
                pass

    # ------------------------------------------------------------------ Group chevrons
    def _chevron_icon(self, opened: bool):
        """Cached expand/collapse chevron for a group-header row, neutral-toned."""
        name = _GROUP_OPEN_ICON if opened else _GROUP_CLOSED_ICON
        return self._marker_icon(name)

    def _toggle_group_open(self, iid) -> None:
        """Flip a group header's open state and swap its chevron to match.

        Setting `open` programmatically does not fire `<<TreeviewOpen/Close>>`,
        so the chevron is updated here directly (the event bindings still cover
        keyboard-driven expand/collapse).
        """
        try:
            new_state = not bool(int(self._tree.item(iid, "open") or 0))
            self._tree.item(iid, open=new_state, image=self._chevron_icon(new_state))
        except Exception:
            pass

    def _refresh_group_chevrons(self, _event=None) -> None:
        """Sync every group header's chevron to its current open/closed state."""
        if not self._group_by_key:
            return
        for iid in self._group_parents.values():
            try:
                opened = bool(int(self._tree.item(iid, "open") or 0))
                img = self._chevron_icon(opened)
                if img is not None:
                    self._tree.item(iid, image=img)
            except Exception:
                pass

    def _rebalance_grouped_widths(self) -> None:
        """Distribute available width across data columns when grouped so the left tree column is included."""
        # Only rebalance when grouping is active and xscroll is off (otherwise user can scroll)
        if not self._group_by_key or self._paging['xscroll']:
            return
        try:
            tree_width = max(0, int(self._tree.winfo_width()))
            group_width = max(0, int(self._tree.column("#0", option="width") or 0))
            vsb_width = 0
            if getattr(self, "_vsb", None):
                try:
                    self._vsb.update_idletasks()
                    if self._vsb.winfo_ismapped():
                        vsb_width = int(self._vsb.winfo_width())
                except Exception:
                    vsb_width = 0
            # Leave a small cushion to avoid oscillating scrollbar
            available = tree_width - group_width - vsb_width - 8
            if available <= 0:
                return
            cols = [c for c in self._display_columns if c < len(self._heading_texts)]
            if not cols:
                return
            width = max(self._column_min_width, available // len(cols))
            for c in cols:
                self._tree.column(c, width=width, stretch=True)
            # Keep the group column fixed so only data columns flex
            self._tree.column("#0", stretch=False)
        except Exception:
            pass

    def _on_tree_configure(self, _event=None) -> None:
        """Handle resize events to keep grouped layouts sized to the available width."""
        self._rebalance_grouped_widths()

    # ------------------------------------------------------------------ Export helpers
    # ------------------------------------------------------------------ Export — data access
    def _export_columns(self) -> tuple[list[str], list[str]]:
        """Return `(header_texts, keys)` for the displayed columns (no internal columns)."""
        _hidden = self._internal_fields()
        keys = [k for k in self._column_keys if k not in _hidden]
        headers = [self._column_heading(k) for k in keys]
        return headers, keys

    def _ds_page_size(self) -> int:
        """Page size used by the data source (matches what `_load_page` renders)."""
        return getattr(self._datasource, "page_size", self._paging['page_size'])

    def _scope_count(self, scope: str) -> int:
        """Number of rows the given scope would export."""
        if scope == "selection":
            return len(self._tree.selection())
        with self._apply_view_to_source():
            if scope == "page":
                psize = self._ds_page_size()
                start = self._current_page * psize
                return len(self._datasource.page_slice(start, psize))
            return self._datasource.count

    def _iter_raw_chunks(self, scope: str, chunk_size: int):
        """Yield lists of raw records for `scope`, paging through large 'all' scopes."""
        if scope == "selection":
            rows = [self._row_map[iid] for iid in self._tree.selection() if iid in self._row_map]
            if rows:
                yield rows
            return
        # The view (this table's filter/sort) is applied to the SHARED source only
        # for the duration of each read, never across a `yield` — otherwise a
        # caller that stops iterating early (e.g. `break`s out of `iter_rows`)
        # would suspend the generator inside the context manager and leave the
        # shared source clobbered until GC, defeating per-view isolation.
        if scope == "page":
            with self._apply_view_to_source():
                psize = self._ds_page_size()
                start = self._current_page * psize
                rows = self._datasource.page_slice(start, psize)
            if rows:
                yield rows
            return
        # 'all' (the filtered/sorted set) — page through so memory stays flat.
        with self._apply_view_to_source():
            total = self._datasource.count
        offset = 0
        while offset < total:
            with self._apply_view_to_source():
                chunk = self._datasource.page_slice(offset, chunk_size)
            if not chunk:
                break
            yield chunk
            offset += len(chunk)

    def _to_delimited(self, rows: list, delimiter: str) -> str:
        """Serialize `rows` (raw records) as delimited text over the displayed columns."""
        import csv
        import io

        headers, keys = self._export_columns()
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=delimiter)
        writer.writerow(headers)
        writer.writerows([[rec.get(k, "") for k in keys] for rec in rows])
        return buf.getvalue()

    def _guard_materialize(self, scope: str, max_rows: int | None) -> None:
        if max_rows is None:
            return
        n = self._scope_count(scope)
        if n > max_rows:
            raise ValueError(
                f"{n} rows exceeds max_rows={max_rows}; use iter_rows() or "
                f"export_file() to stream large exports."
            )

    def to_rows(self, scope: Literal["all", "page", "selection"] = "all", *, max_rows: int | None = _EXPORT_MAX_MATERIALIZE) -> list[dict]:
        """Return the scope's records as a list of dicts (materialized — small data).

        Raises if the row count exceeds `max_rows`; use `iter_rows()` for large data.
        """
        self._guard_materialize(scope, max_rows)
        return [self._public_record(r) for chunk in self._iter_raw_chunks(scope, _EXPORT_CHUNK_SIZE) for r in chunk]

    def to_csv(self, scope: Literal["all", "page", "selection"] = "all", *, max_rows: int | None = _EXPORT_MAX_MATERIALIZE) -> str:
        """Return the scope's data as a CSV string (materialized — small data).

        Raises if the row count exceeds `max_rows`; use `export_file()` for large data.
        """
        self._guard_materialize(scope, max_rows)
        rows = [r for chunk in self._iter_raw_chunks(scope, _EXPORT_CHUNK_SIZE) for r in chunk]
        return self._to_delimited(rows, ",")

    def iter_rows(self, scope: Literal["all", "page", "selection"] = "all", chunk_size: int = _EXPORT_CHUNK_SIZE):
        """Lazily yield the scope's records one at a time, paging the data source."""
        for chunk in self._iter_raw_chunks(scope, chunk_size):
            for rec in chunk:
                yield self._public_record(rec)

    # ------------------------------------------------------------------ Export — file/clipboard
    def _configured_export_formats(self) -> list[str]:
        """The export formats this table offers (the `export_formats` config)."""
        configured = self._exporting.get('formats') or ('csv',)
        return [f for f in configured if f in _EXPORT_FORMATS]

    def _available_export_formats(self) -> list[str]:
        """Configured formats whose optional dependency (if any) is installed."""
        return [f for f in self._configured_export_formats() if _EXPORT_FORMATS[f]["available"]()]

    def _warn_unavailable_export_formats(self) -> None:
        """Warn (developer-facing) about configured formats missing their dependency."""
        for fmt in self._configured_export_formats():
            spec = _EXPORT_FORMATS[fmt]
            if not spec["available"]():
                logger.warning(
                    "DataTable export_formats includes %r, but its dependency is not "
                    "installed (pip install bootstack[%s]); it is hidden from the export "
                    "menu until then.", fmt, spec["extra"],
                )

    def _resolve_format(self, path: str, fmt: str | None) -> str:
        """Resolve the export format from an explicit `fmt` or the path extension.

        Validates against the configured `export_formats` and that the format's
        optional dependency (if any) is installed.
        """
        if fmt:
            name = fmt.lower()
        else:
            ext = os.path.splitext(path)[1].lower()
            name = _EXT_TO_EXPORT_FORMAT.get(ext)
        configured = self._configured_export_formats()
        if name not in _EXPORT_FORMATS or name not in configured:
            raise ValueError(
                f"Export format {name!r} is not enabled. Configured formats: "
                f"{', '.join(configured)}. Add it via export_formats=."
            )
        spec = _EXPORT_FORMATS[name]
        if not spec["available"]():
            raise RuntimeError(
                f"{name} export requires an optional dependency: "
                f"pip install bootstack[{spec['extra']}]."
            )
        return name

    def _make_writer(self, path: str, fmt: str, headers: list[str], keys: list[str]):
        """Open a streaming writer for `fmt`; return `(write_chunk, close)`.

        Both writers append incrementally (csv row-by-row, xlsx in
        constant-memory mode), so the full dataset is never materialized.
        """
        if fmt == "xlsx":
            import xlsxwriter

            workbook = xlsxwriter.Workbook(path, {"constant_memory": True})
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({"bold": True})
            for c, header in enumerate(headers):
                worksheet.write(0, c, header, bold)
            state = {"row": 1}

            def write_chunk(chunk):
                row_idx = state["row"]
                for rec in chunk:
                    for c, key in enumerate(keys):
                        worksheet.write(row_idx, c, rec.get(key))
                    row_idx += 1
                state["row"] = row_idx

            return write_chunk, workbook.close

        import csv

        delimiter = "\t" if fmt == "tsv" else ","
        handle = open(path, "w", newline="", encoding="utf-8")
        writer = csv.writer(handle, delimiter=delimiter)
        writer.writerow(headers)

        def write_chunk(chunk):
            writer.writerows([[rec.get(k, "") for k in keys] for rec in chunk])

        return write_chunk, handle.close

    def export_file(
        self,
        path: str,
        scope: Literal["all", "page", "selection"] = "all",
        *,
        format: str | None = None,
        chunk_size: int = _EXPORT_CHUNK_SIZE,
        on_progress=None,
    ) -> int:
        """Stream the scope's data to `path`, paging so memory stays flat.

        Synchronous. Format is inferred from the path extension unless `format`
        is given. `on_progress(written, total)` is called after each chunk.
        Returns the number of rows written.
        """
        fmt = self._resolve_format(path, format)
        if _EXPORT_FORMATS[fmt]["kind"] == "registry":
            return self._export_file_registry(path, scope, fmt, chunk_size, on_progress)
        headers, keys = self._export_columns()
        total = self._scope_count(scope)
        write_chunk, close = self._make_writer(path, fmt, headers, keys)
        written = 0
        try:
            for chunk in self._iter_raw_chunks(scope, chunk_size):
                write_chunk(chunk)
                written += len(chunk)
                if on_progress is not None:
                    on_progress(written, total)
        finally:
            close()
        self._emit_export(target="file", fmt=fmt, path=path, count=written)
        return written

    def _export_file_registry(self, path, scope, fmt, chunk_size, on_progress) -> int:
        """Synchronously stream a registry-format export over the displayed columns.

        Records are projected to the exported columns (what the table shows) and
        streamed through `bootstack.data.writers`, so the export carries the same
        columns as CSV/XLSX. (For the full record set, use
        `table.data_source.save(path)`.)
        """
        from bootstack.data.writers import write_records

        _headers, keys = self._export_columns()
        total = self._scope_count(scope)
        counter = {"n": 0}

        def _records():
            for chunk in self._iter_raw_chunks(scope, chunk_size):
                for raw in chunk:
                    pub = self._public_record(raw)
                    yield {k: pub.get(k) for k in keys}
                counter["n"] += len(chunk)
                if on_progress is not None:
                    on_progress(counter["n"], total)

        write_records(path, _records(), format=fmt)
        self._emit_export(target="file", fmt=fmt, path=path, count=counter["n"])
        return counter["n"]

    def export_file_async(
        self,
        path: str,
        scope: Literal["all", "page", "selection"] = "all",
        *,
        format: Literal["csv", "tsv", "xlsx"] | None = None,
        chunk_size: int = _EXPORT_CHUNK_SIZE,
        on_progress=None,
        on_done=None,
    ) -> _ExportJob:
        """Stream to `path` without blocking the UI; return a cancelable job.

        Writes one chunk per idle tick. `on_progress(written, total)` fires per
        chunk; `on_done(status, written, error)` fires once at the end with
        `status` in `'completed'` / `'cancelled'` / `'error'`. Cancel or error
        removes the partial file. Call `job.cancel()` to stop.
        """
        fmt = self._resolve_format(path, format)
        if _EXPORT_FORMATS[fmt]["kind"] == "registry":
            raise ValueError(
                f"Async export supports csv/tsv/xlsx; {fmt!r} writes synchronously — "
                f"use export_file()."
            )
        headers, keys = self._export_columns()
        total = self._scope_count(scope)
        write_chunk, close = self._make_writer(path, fmt, headers, keys)
        chunks = self._iter_raw_chunks(scope, chunk_size)

        def _complete(status, written, error):
            self._export_jobs.discard(job)
            if status == "completed":
                self._emit_export(target="file", fmt=fmt, path=path, count=written)
            else:
                try:
                    os.remove(path)
                except OSError:
                    pass
                if status == "error":
                    logger.error("Async export to %s failed", path, exc_info=error)
            if on_done is not None:
                on_done(status, written, error)

        job = _ExportJob(
            self, chunks, write_chunk, close, total,
            on_progress=on_progress, on_complete=_complete,
        )
        self._export_jobs.add(job)
        return job.start()

    def _emit_export(self, *, target: str, fmt: str, path: str | None, count: int, records=None) -> None:
        self.event_generate(
            "<<Export>>",
            data=ExportEvent(count=count, target=target, format=fmt, path=path, records=records or []),
        )

    def _default_scope(self) -> str:
        """Scope for the built-in export actions: the selection if any, else all."""
        if self._exporting.get('allow_export_selection', True) and self._tree.selection():
            return "selection"
        return "all"

    def _update_export_labels(self) -> None:
        """Reflect the implicit export scope (selection vs all) in the menu labels."""
        btn = getattr(self, "_export_btn", None)
        tree = getattr(self, "_tree", None)
        if btn is None or tree is None:
            return
        count = len(tree.selection())
        if self._exporting.get('allow_export_selection', True) and count > 0:
            copy_text = f"Copy selection ({count:,})"
            save_text = f"Save selection ({count:,})"
        else:
            copy_text = "Copy to clipboard"
            save_text = "Save to file"
        try:
            btn.configure_item("export_copy", text=copy_text)
            btn.configure_item("export_save", text=save_text)
        except Exception:
            logger.exception("Failed to update export menu labels")

    def _copy_to_clipboard(self) -> None:
        """Copy the default scope to the clipboard as tab-separated text."""
        scope = self._default_scope()
        rows = [r for chunk in self._iter_raw_chunks(scope, _EXPORT_CHUNK_SIZE) for r in chunk]
        if not rows:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(self._to_delimited(rows, "\t"))
        except Exception:
            logger.exception("Failed to copy table to clipboard")
            return
        self._emit_export(
            target="clipboard", fmt="tsv", path=None, count=len(rows),
            records=[self._public_record(r) for r in rows],
        )

    def _save_to_file(self) -> None:
        """Prompt for a destination and stream the default scope to it.

        Small exports run synchronously (instant); large ones run on the event
        loop with a progress dialog so the UI stays responsive and cancelable.
        """
        from tkinter import filedialog

        available = self._available_export_formats() or ["csv"]
        filetypes = [(_EXPORT_FORMATS[f]["label"], "*" + _EXPORT_FORMATS[f]["ext"]) for f in available]
        filetypes.append(("All files", "*.*"))
        default_fmt = available[0]
        default_ext = _EXPORT_FORMATS[default_fmt]["ext"]

        scope = self._default_scope()
        path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            title=MessageCatalog.translate("table.export"),
            defaultextension=default_ext,
            initialfile="table_export" + default_ext,
            filetypes=filetypes,
        )
        if not path:
            return

        # Registry formats write synchronously; only the cooperative formats
        # (csv/tsv/xlsx) use the async progress path for very large exports.
        try:
            fmt = self._resolve_format(path, None)
        except Exception:
            logger.exception("Failed to resolve export format for %s", path)
            return
        cooperative = _EXPORT_FORMATS[fmt]["kind"] == "cooperative"
        if not cooperative or self._scope_count(scope) <= _EXPORT_ASYNC_THRESHOLD:
            try:
                self.export_file(path, scope=scope)
            except Exception:
                logger.exception("Failed to export table to %s", path)
            return
        self._save_to_file_with_progress(path, scope)

    def _save_to_file_with_progress(self, path: str, scope: str) -> None:
        """Run a large export on the event loop behind a non-blocking progress window.

        The window does not block (no nested loop), so the export's chunk steps
        run on the live main loop and the bar updates as it goes.
        """
        from bootstack._runtime.toplevel import Toplevel

        total = self._scope_count(scope)
        parent = self.winfo_toplevel()
        state: dict = {"job": None, "destroyed": False}

        top = Toplevel(
            title=MessageCatalog.translate("table.export"),
            master=parent,
            transient=parent,
            minsize=(440, 120),
            resizable=(False, False),
            center_on_parent=True,
        )
        frame = Frame(top, padding=14)
        frame.pack(fill="both", expand=True)
        label = Label(frame, text=f"Exporting 0 of {total:,}…")
        label.pack(anchor="w", pady=(0, 8))
        bar = Progressbar(frame, mode="determinate", maximum=max(total, 1), value=0)
        bar.pack(fill="x", pady=(0, 8))
        Label(frame, text="Close this window to cancel.", accent="muted").pack(anchor="w")

        def cancel_export():
            """Cancel the running job (its partial file is removed on cancel)."""
            if state["job"] is not None:
                state["job"].cancel()

        def destroy_window():
            if state["destroyed"]:
                return
            state["destroyed"] = True
            try:
                top.destroy()
            except Exception:
                pass

        def on_progress(written, count):
            if not state["destroyed"]:
                bar.set(written)
                label.configure(text=f"Exporting {written:,} of {count:,}…")

        def on_done(status, written, error):
            destroy_window()
            if status == "error":
                logger.error("Export to %s failed", path, exc_info=error)

        def request_close():
            # Closing the window cancels the export and removes the partial file.
            state["destroyed"] = True
            cancel_export()
            return None

        top.add_close_handler(request_close)
        top.show()  # Toplevel starts withdrawn; reveal it before the export runs.
        state["job"] = self.export_file_async(path, scope, on_progress=on_progress, on_done=on_done)

    # ------------------------------------------------------------------ Header click handling
    def _toggle_select_active(self) -> bool:
        """Whether a plain click should toggle a row (checklist behavior).

        Active whenever the multi-select checkboxes are visible, where users
        expect a click to add/remove a row without holding Ctrl/Shift.
        """
        return self._selection_markers_active()

    def _on_header_click(self, event):
        """Handle left-click: header sorting, or toggle-select with checkboxes."""
        # A left-click on the tree dismisses an open context menu. Do it
        # explicitly: the toggle-select and group-row branches below return
        # 'break', which stops the event before it reaches the window-level
        # outside-click handler that would otherwise close the menu.
        self._dismiss_context_menus()
        region = self._tree.identify_region(event.x, event.y)
        if region == "heading":
            if self._sorting == 'none':
                return None
            col_id = self._tree.identify_column(event.x)  # e.g. "#1"
            try:
                display_idx = int(col_id.strip("#")) - 1
            except Exception:
                return None
            if display_idx < 0 or display_idx >= len(self._display_columns):
                return None
            column_idx = self._display_columns[display_idx]
            self._on_sort(column_idx)
            return None

        # A row with children is expandable — clicking anywhere on it toggles
        # open/closed (the native indicator that used to own this click was
        # removed from the item layout). Leaf rows have no children, so they
        # fall through to normal selection below.
        iid = self._tree.identify_row(event.y)
        if iid and self._tree.get_children(iid):
            self._toggle_group_open(iid)
            return "break"

        # Body click with checkboxes showing: treat the list like a checklist —
        # a plain click toggles the row in/out of the selection (no modifier),
        # and "break" suppresses ttk's default replace-the-selection behavior.
        if self._toggle_select_active():
            iid = self._tree.identify_row(event.y)
            if iid:
                if iid in self._tree.selection():
                    self._tree.selection_remove(iid)
                else:
                    self._tree.selection_add(iid)
            return "break"
        return None

    def _filter_header_column(self) -> None:
        """Show filter dialog for the currently selected header column."""
        col = self._header_menu_col
        if col is None or col >= len(self._column_keys):
            return
        self._show_column_filter_dialog(col)

    def _show_column_filter_dialog(self, column_idx: int) -> None:
        """Show FilterDialog with distinct values for the column."""
        from bootstack.dialogs._impl.filterdialog import FilterDialog

        if column_idx >= len(self._column_keys):
            return

        key = self._column_keys[column_idx]
        heading_text = self._heading_texts[column_idx] if column_idx < len(self._heading_texts) else key

        # Get distinct values from datasource
        try:
            distinct_values = self._datasource.get_distinct_values(key)
        except Exception:
            distinct_values = []

        if not distinct_values:
            return

        empty_text = MessageCatalog.translate("table.empty")
        # Build items for the filter dialog
        current_filter = self._column_filters.get(key)
        items = []
        for val in distinct_values:
            display_text = str(val) if val is not None else empty_text
            selected = current_filter is None or val in current_filter
            items.append(
                {
                    "text": display_text,
                    "value": val,
                    "selected": selected
                })

        # Position dialog below the header
        col_id = f"#{self._display_columns.index(column_idx) + 1}" if column_idx in self._display_columns else "#1"
        pos_x = self._tree.winfo_rootx()
        pos_y = self._tree.winfo_rooty()

        tree_items = self._tree.get_children()
        if tree_items:
            bbox = self._tree.bbox(tree_items[0], col_id)
            if bbox:
                pos_x = self._tree.winfo_rootx() + bbox[0]
                pos_y = self._tree.winfo_rooty() + bbox[1] + 2

        dialog = FilterDialog(
            master=self.winfo_toplevel(),
            title=MessageCatalog.translate("table.filter_column", heading_text),
            items=items,
            enable_search=True,
            enable_select_all=True,
            undecorated=True
        )

        result = dialog.show(position=(pos_x, pos_y))

        if result is not None:
            self._apply_column_filter(key, result, distinct_values)

    def _apply_column_filter(self, key: str, selected_values: list, all_values: list) -> None:
        """Apply column filter based on selected values."""
        # If all values selected, clear the filter for this column
        if set(selected_values) == set(all_values):
            self._column_filters.pop(key, None)
        else:
            self._column_filters[key] = selected_values

        # Build combined WHERE clause from all column filters
        self._rebuild_filter_where()

    def _build_column_filter_condition(self):
        """Build the combined condition from all active column filters (or None)."""
        clauses = []
        for key, values in self._column_filters.items():
            if not values:
                # No values selected = match nothing for this column
                clauses.append(col(key).is_in([]))
                continue
            non_null = [v for v in values if v is not None]
            parts = []
            if non_null:
                parts.append(col(key).is_in(non_null))
            if None in values:
                parts.append(col(key).is_null())
            clause = any_of(*parts)
            if clause is not None:
                clauses.append(clause)
        return all_of(*clauses)

    def _rebuild_filter_where(self) -> None:
        """Re-apply the combined where() after a column filter change."""
        self._apply_where()

    # ------------------------------------------------------------------ Context dispatch
    def _on_tree_context(self, event) -> None:
        if self._context_menus == "none":
            return
        region = self._tree.identify_region(event.x, event.y)
        if region == "heading":
            if not self._header_context_enabled():
                return
            self._on_header_context(event)
        else:
            if not self._row_context_enabled():
                return
            self._on_row_context(event)

    def _on_selection_event(self, _event=None) -> None:
        """Forward selection changes to subscribers."""
        rows = self.selected_rows
        ids = [r.get("id") for r in rows]
        self._update_export_labels()
        self._update_selection_markers()
        self.event_generate("<<SelectionChange>>", data=SelectionEvent(records=rows, ids=ids))

    def _on_row_click_event(self, event) -> None:
        region = self._tree.identify_region(event.x, event.y)
        if region == "heading":
            return
        iid = self._tree.identify_row(event.y)
        if not iid or iid not in self._row_map:
            return  # empty space or a group-header row (no record)
        rec = self._row_map.get(iid, {})
        self.event_generate("<<RowClick>>", data=RowEvent(record=self._public_record(rec), id=self._record_id(rec)))

    # ------------------------------------------------------------------ Header context menu
    def _ensure_header_menu(self) -> None:
        if not self._header_context_enabled():
            return
        if self._header_menu:
            return
        menu = ContextMenu(master=self, target=self._tree, trigger=None)
        menu.add_command(text="table.align_left", icon="align-start", command=self._align_header_left)
        menu.add_command(text="table.align_center", icon="align-center", command=self._align_header_center)
        menu.add_command(text="table.align_right", icon="align-end", command=self._align_header_right)
        menu.add_separator()
        menu.add_command(text="table.move_left", icon="arrow-left", command=self._move_header_left)
        menu.add_command(text="table.move_right", icon="arrow-right", command=self._move_header_right)
        menu.add_command(text="table.move_first", icon="arrow-bar-left", command=self._move_header_first)
        menu.add_command(text="table.move_last", icon="arrow-bar-right", command=self._move_header_last)
        menu.add_separator()
        menu.add_command(text="table.hide_column", icon="eye-slash", command=self._hide_header_column)
        menu.add_command(text="table.show_all", icon="eye", command=self._show_all_columns)
        if self._allow_grouping:
            menu.add_separator()
            menu.add_command(text="table.group_by_column", command=self._group_header_column)
            menu.add_command(text="table.ungroup_all", command=self._ungroup_all)
        menu.add_separator()
        menu.add_command(text="table.reset", icon="arrow-counterclockwise", command=self._reset_table)
        menu.add_separator()
        if not self._sorting == 'none':
            menu.add_command(text="table.clear_sort", icon="x-lg", command=self._clear_sort)
        self._header_menu = menu

    def _on_header_context(self, event) -> None:
        if not self._header_context_enabled():
            return
        # Only handle header clicks
        if self._tree.identify_region(event.x, event.y) != "heading":
            return
        col_id = self._tree.identify_column(event.x)  # e.g. "#1"
        try:
            idx = int(col_id.strip("#")) - 1
        except Exception:
            return
        if idx < 0 or idx >= len(self._display_columns):
            return
        self._header_menu_col = self._display_columns[idx]
        self._ensure_header_menu()

        # Try to position at bottom-left of the clicked header
        pos_x, pos_y = event.x_root, event.y_root
        items = self._tree.get_children()
        if items:
            bbox = self._tree.bbox(items[0], col_id)
            if bbox:
                # bbox is relative to the widget; bbox[1] is header height offset
                pos_x = self._tree.winfo_rootx() + bbox[0]
                pos_y = self._tree.winfo_rooty() + bbox[1] + 2
        self._header_menu.show(position=(pos_x, pos_y))

    def _align_header_left(self) -> None:
        self._set_heading_anchor("w")

    def _align_header_center(self) -> None:
        self._set_heading_anchor("center")

    def _align_header_right(self) -> None:
        self._set_heading_anchor("e")

    def _set_heading_anchor(self, anchor: str) -> None:
        """Align only the header text for the selected column."""
        col = self._header_menu_col
        if col is None:
            return
        self._tree.heading(col, anchor=anchor)
        self._tree.column(col, anchor=anchor)

    def _move_header_left(self) -> None:
        self._move_column(-1)

    def _move_header_right(self) -> None:
        self._move_column(1)

    def _move_header_first(self) -> None:
        self._move_column(to_index=0)

    def _move_header_last(self) -> None:
        self._move_column(to_index=len(self._display_columns) - 1)

    def _move_column(self, delta: int | None = None, to_index: int | None = None) -> None:
        col = self._header_menu_col
        if col is None or col not in self._display_columns:
            return
        current_pos = self._display_columns.index(col)
        if to_index is not None:
            new_pos = max(0, min(len(self._display_columns) - 1, to_index))
        else:
            new_pos = current_pos + (delta or 0)
        new_pos = max(0, min(len(self._display_columns) - 1, new_pos))
        if new_pos == current_pos:
            return
        self._display_columns.pop(current_pos)
        self._display_columns.insert(new_pos, col)
        self._tree.configure(displaycolumns=self._display_columns)

    def _hide_header_column(self) -> None:
        col = self._header_menu_col
        if col is None or col not in self._display_columns:
            return
        self._display_columns.remove(col)
        if not self._display_columns:
            self._display_columns = list(range(len(self._heading_texts)))
        self._tree.configure(displaycolumns=self._display_columns)

    def _show_all_columns(self) -> None:
        if not self._heading_texts:
            return
        self._display_columns = list(range(len(self._heading_texts)))
        self._tree.configure(displaycolumns=self._display_columns)

    def _show_column_chooser_dialog(self) -> None:
        """Show a dialog to select which columns are visible."""
        from bootstack.dialogs._impl.filterdialog import FilterDialog

        if not self._heading_texts:
            return

        # Build items for the filter dialog
        items = []
        for idx, text in enumerate(self._heading_texts):
            items.append(
                {
                    "text": text,
                    "value": idx,
                    "selected": idx in self._display_columns
                })

        # Calculate position: align dialog's top-right to button's bottom-right
        btn = self._column_chooser_btn
        btn.update_idletasks()
        btn_right = btn.winfo_rootx() + btn.winfo_width()
        btn_bottom = btn.winfo_rooty() + btn.winfo_height()
        dialog_width = 250  # FilterDialog has fixed width of 250
        pos_x = btn_right - dialog_width - 2  # 2px west
        pos_y = btn_bottom + 2  # 2px south

        dialog = FilterDialog(
            master=self.winfo_toplevel(),
            title="Columns",
            items=items,
            enable_search=False,
            enable_select_all=True,
            undecorated=True
        )

        self._active_chooser_dialog = dialog
        try:
            result = dialog.show(position=(pos_x, pos_y))
        finally:
            self._active_chooser_dialog = None

        if result is not None:
            # Update display columns based on selection
            self._display_columns = [idx for idx in result if isinstance(idx, int)]
            if not self._display_columns:
                # Ensure at least one column is visible
                self._display_columns = list(range(len(self._heading_texts)))
            self._tree.configure(displaycolumns=self._display_columns)

    def _reset_table(self) -> None:
        # Reset sort, columns visibility/order, and reload first page
        self._display_columns = list(range(len(self._heading_texts)))
        self._tree.configure(displaycolumns=self._display_columns)
        self._clear_sort()

    # ------------------------------------------------------------------ Grouping
    def _group_header_column(self) -> None:
        """Group current view by the selected header column."""
        col = self._header_menu_col
        if col is None or col >= len(self._column_keys):
            return
        key = self._column_keys[col]
        self._group_by_key = key
        self._group_parents.clear()
        self._sort_state = {key: True}
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)
        self._update_status_labels()

    def _ungroup_all(self) -> None:
        """Return to flat view."""
        if not self._group_by_key:
            return
        self._group_by_key = None
        self._group_parents.clear()
        self._apply_group_show_state(False)
        self._load_page(self._current_page)
        self._update_status_labels()

    def _grouping_primary_index(self) -> int | None:
        """Display column promoted into the tree column (#0) while grouped.

        The first visible column that isn't the group-by column: its values move
        into #0 (indented under the group headers), so #0 becomes a real data
        column rather than a reserved group-only column.
        """
        if not self._group_by_key or self._group_by_key not in self._column_keys:
            return None
        group_idx = self._column_keys.index(self._group_by_key)
        for c in self._display_columns:
            if c != group_idx:
                return c
        return None

    def _apply_group_show_state(self, grouped: bool) -> None:
        """Toggle tree column visibility when grouping."""
        if grouped:
            self._tree.configure(show="tree headings")
            group_idx = self._column_keys.index(self._group_by_key)
            primary = self._grouping_primary_index()
            # #0 becomes the first non-group column: take its heading + width, and
            # drop both it and the group column out of the value columns (the group
            # appears as the header rows; the primary appears in #0).
            if primary is not None:
                heading_text = self._heading_texts[primary] if primary < len(self._heading_texts) else ""
                try:
                    width = int(self._tree.column(primary, option="width")) or 200
                except Exception:
                    width = 200
                self._tree.heading("#0", text=heading_text, anchor="w")
                self._tree.column("#0", width=max(width, 160), minwidth=120, anchor="w", stretch=False)
            else:
                self._tree.heading("#0", text="", anchor="w")
                self._tree.column("#0", width=200, minwidth=120, anchor="w", stretch=False)
            try:
                hidden = {group_idx, primary}
                visible = [c for c in self._display_columns if c not in hidden]
                self._tree.configure(displaycolumns=visible or self._display_columns)
            except Exception:
                pass
            try:
                # Reset horizontal view so the group column is not scrolled out
                self._tree.xview_moveto(0)
            except Exception:
                pass
            self._rebalance_grouped_widths()
        elif self._selection_markers_active():
            # Reveal a narrow tree column to host the per-row selection marker.
            self._tree.configure(show="tree headings")
            self._tree.heading("#0", text="")
            marker_w = self._marker_column_width()
            self._tree.column("#0", width=marker_w, minwidth=marker_w, anchor="center", stretch=False)
            self._restore_data_columns()
        else:
            self._tree.configure(show="headings")
            # Keep the tree column narrow/inert when unused
            self._tree.heading("#0", text="")
            self._tree.column("#0", width=0, minwidth=0, stretch=False)
            self._restore_data_columns()

    def _restore_data_columns(self) -> None:
        """Show the full set of data columns (used when not grouped)."""
        try:
            self._tree.configure(displaycolumns=self._display_columns)
        except Exception:
            pass
        try:
            stretch_cols = not self._paging['xscroll']
            for idx in range(len(self._heading_texts)):
                self._tree.column(idx, stretch=stretch_cols)
        except Exception:
            pass

    # ------------------------------------------------------------------ Cell formatting
    def _column_formatter(self, idx: int):
        """Resolve (and cache) a column's display formatter callable, or None.

        A column's `format` may be a format-spec string (applied as
        `spec.format(value)`) or a callable `(value) -> str`.
        """
        if idx in self._column_formats:
            return self._column_formats[idx]
        formatter = None
        if 0 <= idx < len(self._column_defs):
            coldef = self._column_defs[idx]
            if isinstance(coldef, dict):
                spec = coldef.get("format")
                if callable(spec):
                    formatter = spec
                elif isinstance(spec, str) and spec:
                    formatter = (lambda s: (lambda v: s.format(v)))(spec)
        self._column_formats[idx] = formatter
        return formatter

    def _format_cell(self, idx: int, value):
        """Apply a column's display formatter to a value (raw value on failure)."""
        if value is None or value == "":
            return value
        formatter = self._column_formatter(idx)
        if formatter is None:
            return value
        try:
            return formatter(value)
        except Exception:
            return value

    def _display_values(self, rec: dict) -> list:
        """Build the formatted value row for display (record stays raw in _row_map)."""
        return [self._format_cell(i, rec.get(k, "")) for i, k in enumerate(self._column_keys)]

    def _render_flat(self, records: list[dict]) -> None:
        """Insert records as flat rows."""
        stripe = self._row_alternation.get('enabled', False) and not self._group_by_key
        for idx, rec in enumerate(records):
            values = self._display_values(rec)
            tags = ("altrow",) if stripe and idx % 2 == 1 else ()
            iid = self._tree.insert("", "end", values=values, tags=tags)
            self._row_map[iid] = rec

    def _render_grouped(self, records: list[dict]) -> None:
        """Insert records under group-header nodes.

        Group headers are root-level nodes whose label sits in the tree column
        (#0). Each child carries its primary field (the first non-group column)
        as #0 text — indented under its group — with the full record kept in the
        value columns (the primary + group columns are hidden from those).
        """
        key = self._group_by_key
        if not key or key not in self._column_keys:
            self._render_flat(records)
            return
        primary_idx = self._grouping_primary_index()
        primary_key = self._column_keys[primary_idx] if primary_idx is not None else None
        groups: OrderedDict[str | None, list[dict]] = OrderedDict()
        for rec in records:
            groups.setdefault(rec.get(key), []).append(rec)
        self._group_parents.clear()
        for val, items in groups.items():
            label_val = "(None)" if val is None else str(val)
            label = f"{label_val} ({len(items)})"
            parent_iid = self._tree.insert(
                "", "end", text=label, open=True, image=self._chevron_icon(True)
            )
            self._group_parents[val] = parent_iid
            # Transparent stand-in the same size as the chevron, so a child's
            # depth-indent isn't cancelled out by the parent's chevron width
            # (keeps the child names visibly nested under their group).
            leaf_image = self._marker_icon(None)
            for rec in items:
                values = self._display_values(rec)
                primary_text = "" if primary_idx is None else str(
                    self._format_cell(primary_idx, rec.get(primary_key, ""))
                )
                iid = self._tree.insert(
                    parent_iid, "end", text=primary_text, values=values, image=leaf_image
                )
                self._row_map[iid] = rec

    def _clear_sort(self) -> None:
        self._sort_state.clear()
        self._clear_cache()
        self._update_heading_icons()
        self._load_page(0)
        self._update_status_labels()


# Backwards-compatible alias for the legacy Tableview name
Tableview = TableView
