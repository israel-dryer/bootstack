DataTable
=========

A feature-rich data table with sorting, search, column filters, grouping, paging,
inline editing, and data export. Backed by an in-memory ``SqliteDataSource`` by
default — supply ``rows=`` to pre-load data, or pass any shared ``data_source=``.

.. image:: /_static/examples/datatable-hero-light.png
   :class: bs-screenshot-light
   :alt: DataTable — light theme

.. image:: /_static/examples/datatable-hero-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable — dark theme

Usage
-----

Columns and rows
~~~~~~~~~~~~~~~~

Define columns with ``columns=`` — a list of key strings (which double as
headers), or dicts for control over the header text and width. ``rows=``
pre-loads the data as a list of dicts:

.. code-block:: python

   # Simple: column keys are used as headers
   bs.DataTable(columns=["name", "role", "dept"], rows=people)

   # Dicts give a display header and a width
   bs.DataTable(
       columns=[
           {"text": "Name",   "key": "name",   "width": 160},
           {"text": "Role",   "key": "role",   "width": 150},
           {"text": "Salary", "key": "salary", "width": 100},
       ],
       rows=people,
   )

Format cell values for display with ``format`` — a format-spec string applied as
``spec.format(value)``, or a callable ``(value) -> str`` — and align cells with
``anchor`` (``'w'``, ``'center'``, ``'e'``). Formatting is **display only**:
sorting, filtering, editing, and export all use the underlying value, so a
currency-formatted ``salary`` column still sorts numerically:

.. code-block:: python

   bs.DataTable(
       columns=[
           {"text": "Name",   "key": "name"},
           {"text": "Salary", "key": "salary", "anchor": "e", "format": "${:,.0f}"},
           {"text": "Bonus",  "key": "bonus",  "format": lambda v: f"{v:.1%}"},
       ],
       rows=people,
   )

A column dict (a ``ColumnSpec``) also controls how the column behaves in the
built-in add/edit dialog — the ``editor`` and its ``editor_options``, the value
``dtype`` (which also drives alignment), and ``readonly`` / ``required``:

.. code-block:: python

   bs.DataTable(
       columns=[
           {"key": "name", "required": True},
           {"key": "dept", "editor": "select",
            "editor_options": {"items": ["Engineering", "Design", "Sales"]}},
           {"key": "salary", "dtype": "int"},
           {"key": "id", "readonly": True},
       ],
       rows=people,
   )

The full set of ``ColumnSpec`` keys:

``key``
    Record field the column reads and writes. The only required key.
``text``
    Header label. Defaults to ``key``.
``width`` / ``minwidth``
    Column width and minimum width, in pixels.
``anchor``
    Cell alignment — ``'w'``, ``'center'``, or ``'e'``.
``format``
    Display formatter — a format-spec string (e.g. ``'${:,.0f}'``) or a callable
    ``(value) -> str``. Display only.
``dtype``
    Value type hint (e.g. ``'int'``, ``'text'``) — drives alignment and the
    dialog editor.
``editor`` / ``editor_options``
    Field type and keyword options used in the add/edit dialog.
``readonly`` / ``required``
    Make the column non-editable, or require a value, in the add/edit dialog.

Each record carries a stable ``id`` that events and the selection API use to
identify rows. If your records already have an ``id`` field, that value *is* the
row id — so ``select_rows``, ``update_rows`` / ``delete_rows``, and the row
events all round-trip your own ids (a database key, a UUID). Records without one
get an id assigned automatically. Point at a different field with
``id_field="employee_id"``, and replace the whole dataset later with
``table.set_rows(rows)``.

Column visibility
~~~~~~~~~~~~~~~~~

Show or hide columns at runtime. ``show_column_chooser=True`` adds a toolbar
button that opens a dialog for toggling which columns are visible; individual
columns can also be hidden from the column-header right-click menu:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, show_column_chooser=True)

.. image:: /_static/examples/datatable-column-chooser-light.png
   :class: bs-screenshot-light
   :alt: DataTable column chooser — light theme

.. image:: /_static/examples/datatable-column-chooser-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable column chooser — dark theme

Selection
~~~~~~~~~

``selection_mode`` is ``'single'`` (default), ``'multi'``, or ``'none'``. Read the
current selection with ``selected_rows`` and react with ``on_selection_changed``,
whose :class:`SelectionEvent <bootstack.events.SelectionEvent>` carries the
selected ``records`` and their ``ids``:

.. code-block:: python

   table = bs.DataTable(columns=cols, rows=people, selection_mode="multi")
   table.on_selection_changed(lambda e: print(e.records, e.ids))
   print(table.selected_rows)

Manage the selection programmatically. Users can also press ``Escape`` over the
table to clear it — handy in single-select mode, where clicking cannot return to
an empty selection:

.. code-block:: python

   table.select_all()
   table.select_rows([3, 7])     # by record id
   table.deselect_rows([3])
   table.clear_selection()

In multi-select mode, ``show_selection_controls=True`` adds a per-row checkbox in
the leading column — filled with the accent when selected, a muted outline
otherwise. With the checkboxes visible the table reads as a checklist: a plain
click toggles a row in or out of the selection, no ``Ctrl`` / ``Shift`` needed:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, selection_mode="multi",
            show_selection_controls=True)

.. image:: /_static/examples/datatable-selection-light.png
   :class: bs-screenshot-light
   :alt: DataTable multi-select — light theme

.. image:: /_static/examples/datatable-selection-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable multi-select — dark theme

Searching
~~~~~~~~~

``searchable=True`` (the default) shows a search box that filters across all
columns. Drive it programmatically too:

.. code-block:: python

   table = bs.DataTable(columns=cols, rows=people, searchable=True)
   table.set_search("engineer")
   print(table.get_search())     # "engineer"
   table.clear_search()

.. image:: /_static/examples/datatable-search-light.png
   :class: bs-screenshot-light
   :alt: DataTable search — light theme

.. image:: /_static/examples/datatable-search-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable search — dark theme

Column filters
~~~~~~~~~~~~~~

Beyond free-text search, each column header offers a value filter, and the row
right-click menu adds *filter by cell's value* alongside sort, hide, and delete
actions. Search and column filters compose (both must match) and the status bar
summarizes what's active:

.. image:: /_static/examples/datatable-row-menu-light.png
   :class: bs-screenshot-light
   :alt: DataTable row context menu — light theme

.. image:: /_static/examples/datatable-row-menu-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable row context menu — dark theme

.. code-block:: python

   table = bs.DataTable(columns=cols, rows=people, allow_filter=True)

   table.set_filter("dept", ["Engineering"])   # set one programmatically
   print(table.get_filters())                  # {"dept": ["Engineering"]}
   table.clear_filters()                        # leaves the search term intact

The filters are built on the data source's query API — see
:doc:`../reference/data-sources` for the ``col()`` expression DSL behind them.

.. image:: /_static/examples/datatable-filter-light.png
   :class: bs-screenshot-light
   :alt: DataTable column filter — light theme

.. image:: /_static/examples/datatable-filter-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable column filter — dark theme

Sorting
~~~~~~~

Click a column header to sort; click again to reverse. ``sorting_mode='none'``
disables it:

.. code-block:: python

   table = bs.DataTable(columns=cols, rows=people, sorting_mode="single")

   table.sort_by("salary", ascending=False)
   print(table.get_sorting())    # {"salary": False}  (descending)
   table.clear_sorting()

.. image:: /_static/examples/datatable-sort-light.png
   :class: bs-screenshot-light
   :alt: DataTable sorted column — light theme

.. image:: /_static/examples/datatable-sort-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable sorted column — dark theme

Grouping
~~~~~~~~

Right-click a column header for its context menu — align, reorder, hide/show
columns, clear the sort, and (with ``allow_group=True``) group rows by that
column:

.. image:: /_static/examples/datatable-header-menu-light.png
   :class: bs-screenshot-light
   :alt: DataTable column header menu — light theme

.. image:: /_static/examples/datatable-header-menu-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable column header menu — dark theme

.. code-block:: python

   table = bs.DataTable(columns=cols, rows=people, allow_group=True)

   table.group_by("dept")
   table.expand_all()            # or collapse_all()
   print(table.get_grouping())   # "dept"
   table.clear_grouping()

.. image:: /_static/examples/datatable-group-light.png
   :class: bs-screenshot-light
   :alt: DataTable grouped rows — light theme

.. image:: /_static/examples/datatable-group-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable grouped rows — dark theme

Paging
~~~~~~

Data is paged. ``page_size`` sets the rows per page (default ``25``);
``paging_mode='virtual'`` swaps the pager for infinite scrolling that fetches
more as you scroll:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, page_size=50)
   bs.DataTable(columns=cols, rows=people, paging_mode="virtual")

Navigate pages programmatically:

.. code-block:: python

   table.next_page()
   table.prev_page()
   table.go_to_page(3)
   print(table.current_page, "of", table.page_count)

Editing
~~~~~~~

Enable the built-in editing UI with ``allow_add`` / ``allow_edit`` /
``allow_delete``. The usual way to edit a row is to **double-click it**, which
opens its edit dialog; toolbar buttons and a row right-click menu do the same.
All open the same form dialogs, which validate input and persist to the data
source:

* **Double-click a row** — opens its edit dialog (the primary edit gesture;
  needs ``allow_edit``).
* **Toolbar buttons** — Add, Edit, and Delete.
* **Row right-click menu** — Edit and Delete entries.

.. code-block:: python

   table = bs.DataTable(
       columns=cols, rows=people,
       allow_add=True, allow_edit=True, allow_delete=True,
   )

.. image:: /_static/examples/datatable-edit-light.png
   :class: bs-screenshot-light
   :alt: DataTable edit record dialog — light theme

.. image:: /_static/examples/datatable-edit-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable edit record dialog — dark theme

Mutate programmatically with ``insert_rows`` / ``update_rows`` / ``delete_rows``,
and react with the row events — each fires **once per call** with a
:class:`RowsEvent <bootstack.events.RowsEvent>` carrying all affected
``records`` (so inserting 6,000 rows in one call is a single event, not 6,000):

.. code-block:: python

   table.insert_rows([{"name": "New Hire", "role": "Intern"}])
   table.update_rows([{"id": 3, "role": "Lead"}])   # each dict needs an id
   table.delete_rows([7])                            # by id or record dict

   table.on_rows_insert(lambda e: print("added",   e.records))
   table.on_rows_update(lambda e: print("changed", e.records))
   table.on_rows_delete(lambda e: print("removed", e.records))

To *replace* the whole dataset, prefer ``set_rows(rows)`` — it bulk-loads in a
single pass rather than inserting row by row.

Open the built-in dialogs from your own code with ``new_row()`` and
``edit_row()`` — they honor each column's editor configuration (see
``ColumnSpec`` above), fire the same row events on save, and also return the
saved record:

.. code-block:: python

   table.new_row()                          # New Record dialog
   table.new_row({"dept": "Engineering"})   # pre-filled
   saved = table.edit_row(3)                # Edit dialog for the row with id 3

The add and edit dialogs are built from :doc:`form fields <forms>`; tune their
layout with the ``form=`` constructor option (a ``FormOptions`` dict —
``col_count``, ``min_col_width``, ``scrollable``, ``resizable``).

Row events
~~~~~~~~~~

Row interactions deliver a :class:`RowEvent <bootstack.events.RowEvent>` with the
row's ``record`` dict and its ``id`` (reordering through the row menu fires
``on_rows_move`` with a :class:`RowsEvent <bootstack.events.RowsEvent>` instead).
As with every widget, an ``on_*`` method returns a ``Subscription`` when given a
handler, or a ``Stream`` when called without one:

.. code-block:: python

   table.on_row_click(lambda e: print(e.record, e.id))
   table.on_row_double_click(lambda e: open_detail(e.record))
   table.on_row_right_click(lambda e: ...)
   table.on_rows_move(lambda e: print("reordered", e.records))

   sub = table.on_row_click(lambda e: ...)
   sub.cancel()     # unsubscribe (any on_* returns a Subscription)

With ``allow_edit``, a double-click also opens the row's edit dialog, so
``on_row_double_click`` fires alongside the editor.

Exporting
~~~~~~~~~

``allow_export=True`` adds an export menu with **Copy to clipboard** and **Save to
file** (CSV, plus Excel when the optional ``bootstack[excel]`` extra is installed).
The actions export the selected rows if any are selected, otherwise the whole
filtered set.

.. image:: /_static/examples/datatable-export-light.png
   :class: bs-screenshot-light
   :alt: DataTable export menu — light theme

.. image:: /_static/examples/datatable-export-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable export menu — dark theme

For programmatic export, two tiers cover small and large data. *Materialized*
helpers load everything into memory — convenient for small result sets:

.. code-block:: python

   rows = table.to_rows()        # list[dict]
   text = table.to_csv()         # CSV string

They raise above ``max_rows`` (100,000 by default), a signpost to the streaming
API. *Streaming* helpers page the data source so memory stays flat regardless of
size:

.. code-block:: python

   for record in table.iter_rows():     # lazy, pages the source
       ...

   table.export_file("people.csv")      # streams to disk; .xlsx if bootstack[excel]

For very large exports, ``export_file_async`` runs on the event loop without
blocking the UI, reporting progress and supporting cancellation (a cancelled or
failed export removes the partial file):

.. code-block:: python

   job = table.export_file_async(
       "people.xlsx",
       on_progress=lambda done, total: update_bar(done, total),
       on_done=lambda status, n, err: print(status, n),
   )
   job.cancel()

Every export emits an :class:`ExportEvent <bootstack.events.ExportEvent>`, and
``scope`` selects what to export (``"all"``, ``"page"``, or ``"selection"``):

.. code-block:: python

   table.on_export(lambda e: toast(f"Exported {e.count} rows to {e.path}"))
   table.to_csv(scope="selection")

Data binding
~~~~~~~~~~~~

By default the table builds its own in-memory ``SqliteDataSource``. To back it
with a database file — or to share one source across views — pass a source via
``data_source=``. Mutate that source (even from a background thread) and the
table refreshes itself:

.. code-block:: python

   ds = bs.SqliteDataSource("people.db")
   ds.load(people)

   table = bs.DataTable(columns=cols, data_source=ds)
   ds.insert({"name": "Streamed in"})   # the table updates on its own

Any source that implements the data-source protocol works — ``SqliteDataSource``,
``MemoryDataSource``, ``FileDataSource``, or your own — so row identity,
selection, and editing round-trip regardless of the backend. See
:doc:`../reference/data-sources` for the source's filtering and sorting
(``where()`` / ``order()``) and change broadcasting (``on_change`` / ``observe``).

Density and striping
~~~~~~~~~~~~~~~~~~~~~

Rows are striped by default — pass ``striped=False`` to turn the alternating
background off. ``density='compact'`` tightens the row height, body font, and
cell padding to fit more rows in the same space:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, density="compact")

.. image:: /_static/examples/datatable-density-light.png
   :class: bs-screenshot-light
   :alt: DataTable compact density — light theme

.. image:: /_static/examples/datatable-density-dark.png
   :class: bs-screenshot-dark
   :alt: DataTable compact density — dark theme

The table draws no border of its own. Wrap it in a :doc:`card` or a ``Frame``
when you want a bordered, contained look.

Status bar and context menus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The footer status bar carries the active filter/sort/group summary and the pager.
It is self-managing: the pager hides on a single page and the whole bar collapses
when there is nothing to show. Pass ``show_status_bar=False`` to hide it outright:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, show_status_bar=False)

``context_menus`` controls the right-click menus shown earlier — the column-header
menu (sort, align, reorder, hide, group) and the row menu (filter by value, edit,
delete). Choose ``'all'`` (default), ``'headers'``, ``'rows'``, or ``'none'`` to
disable them:

.. code-block:: python

   bs.DataTable(columns=cols, rows=people, context_menus="headers")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`listview` — a lightweight virtual list for simpler, card-style records.
* :doc:`forms` — the form fields behind the inline add/edit dialogs.
* :doc:`../reference/data-sources` — the data layer, the ``col()`` query DSL, and
  change broadcasting.
* :doc:`../reference/events` — the ``RowEvent``, ``SelectionEvent``, and
  ``ExportEvent`` payloads.

API
---

.. autoclass:: bootstack.widgets.datatable.Table
   :members:
   :undoc-members:

The column and form configuration dicts, and the handle returned by
``export_file_async``:

.. autoclass:: bootstack.widgets.datatable.ColumnSpec
   :members:

.. autoclass:: bootstack.widgets.datatable.FormOptions
   :members:

.. autoclass:: bootstack.widgets.datatable.ExportJob
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/datatable.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
