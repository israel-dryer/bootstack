Table
=====

A feature-rich data table with sorting, search, column filters, grouping, paging,
inline editing, and data export. Backed by an in-memory ``SqliteDataSource`` —
supply ``rows=`` to pre-load data, or pass a shared ``data_source=``.

.. image:: /_static/examples/table-hero-light.png
   :class: bs-screenshot-light
   :alt: Table — light theme

.. image:: /_static/examples/table-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Table — dark theme

Usage
-----

Columns and rows
~~~~~~~~~~~~~~~~

Define columns with ``columns=`` — a list of key strings (which double as
headers), or dicts for control over the header text and width. ``rows=``
pre-loads the data as a list of dicts:

.. code-block:: python

   # Simple: column keys are used as headers
   bs.Table(columns=["name", "role", "dept"], rows=people)

   # Dicts give a display header and a width
   bs.Table(
       columns=[
           {"text": "Name",   "key": "name",   "width": 160},
           {"text": "Role",   "key": "role",   "width": 150},
           {"text": "Salary", "key": "salary", "width": 100},
       ],
       rows=people,
   )

A column dict (a ``ColumnSpec``) also controls how the column behaves in the
built-in add/edit dialog — the ``editor`` and its ``editor_options``, the value
``dtype`` (which also drives alignment), and ``readonly`` / ``required``:

.. code-block:: python

   bs.Table(
       columns=[
           {"key": "name", "required": True},
           {"key": "dept", "editor": "select",
            "editor_options": {"items": ["Engineering", "Design", "Sales"]}},
           {"key": "salary", "dtype": "int"},
           {"key": "id", "readonly": True},
       ],
       rows=people,
   )

Each record carries a stable ``id`` (assigned by the data source) that events and
the selection API use to identify rows. Replace the whole dataset later with
``table.set_rows(rows)``.

Selection
~~~~~~~~~

``selection_mode`` is ``'single'`` (default), ``'multi'``, or ``'none'``. Read the
current selection with ``selected_rows`` and react with ``on_selection_changed``,
whose event carries the selected ``records`` and their ``ids``:

.. code-block:: python

   table = bs.Table(columns=cols, rows=people, selection_mode="multi")
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

.. image:: /_static/examples/table-selection-light.png
   :class: bs-screenshot-light
   :alt: Table multi-select — light theme

.. image:: /_static/examples/table-selection-dark.png
   :class: bs-screenshot-dark
   :alt: Table multi-select — dark theme

Searching
~~~~~~~~~

``searchable=True`` (the default) shows a search box that filters across all
columns. Drive it programmatically too:

.. code-block:: python

   table = bs.Table(columns=cols, rows=people, searchable=True)
   table.set_search("engineer")
   print(table.get_search())     # "engineer"
   table.clear_search()

.. image:: /_static/examples/table-search-light.png
   :class: bs-screenshot-light
   :alt: Table search — light theme

.. image:: /_static/examples/table-search-dark.png
   :class: bs-screenshot-dark
   :alt: Table search — dark theme

Column filters
~~~~~~~~~~~~~~

Beyond free-text search, each column header offers a value filter, and the row
right-click menu adds *filter by cell's value* alongside sort, hide, and delete
actions. Search and column filters compose (both must match) and the status bar
summarizes what's active:

.. image:: /_static/examples/table-row-menu-light.png
   :class: bs-screenshot-light
   :alt: Table row context menu — light theme

.. image:: /_static/examples/table-row-menu-dark.png
   :class: bs-screenshot-dark
   :alt: Table row context menu — dark theme

.. code-block:: python

   bs.Table(columns=cols, rows=people, allow_filter=True)

   table.set_filter("dept", ["Engineering"])   # set one programmatically
   print(table.get_filters())                  # {"dept": ["Engineering"]}
   table.clear_filters()                        # leaves the search term intact

The filters are built on the data source's query API — see
:doc:`../reference/data-sources` for the ``col()`` expression DSL behind them.

.. image:: /_static/examples/table-filter-light.png
   :class: bs-screenshot-light
   :alt: Table column filter — light theme

.. image:: /_static/examples/table-filter-dark.png
   :class: bs-screenshot-dark
   :alt: Table column filter — dark theme

Sorting
~~~~~~~

Click a column header to sort; click again to reverse. ``sorting_mode='none'``
disables it:

.. code-block:: python

   bs.Table(columns=cols, rows=people, sorting_mode="single")

   table.sort_by("salary", ascending=False)
   print(table.get_sorting())    # {"salary": False}  (descending)
   table.clear_sorting()

.. image:: /_static/examples/table-sort-light.png
   :class: bs-screenshot-light
   :alt: Table sorted column — light theme

.. image:: /_static/examples/table-sort-dark.png
   :class: bs-screenshot-dark
   :alt: Table sorted column — dark theme

Grouping
~~~~~~~~

Right-click a column header for its context menu — align, reorder, hide/show
columns, clear the sort, and (with ``allow_group=True``) group rows by that
column:

.. image:: /_static/examples/table-header-menu-light.png
   :class: bs-screenshot-light
   :alt: Table column header menu — light theme

.. image:: /_static/examples/table-header-menu-dark.png
   :class: bs-screenshot-dark
   :alt: Table column header menu — dark theme

.. code-block:: python

   bs.Table(columns=cols, rows=people, allow_group=True)

   table.group_by("dept")
   table.expand_all()            # or collapse_all()
   print(table.get_grouping())   # "dept"
   table.clear_grouping()

.. image:: /_static/examples/table-group-light.png
   :class: bs-screenshot-light
   :alt: Table grouped rows — light theme

.. image:: /_static/examples/table-group-dark.png
   :class: bs-screenshot-dark
   :alt: Table grouped rows — dark theme

Paging
~~~~~~

Data is paged. ``page_size`` sets the rows per page (default ``25``);
``paging_mode='virtual'`` swaps the pager for infinite scrolling that fetches
more as you scroll:

.. code-block:: python

   bs.Table(columns=cols, rows=people, page_size=50)
   bs.Table(columns=cols, rows=people, paging_mode="virtual")

Navigate pages programmatically:

.. code-block:: python

   table.next_page()
   table.prev_page()
   table.go_to_page(3)
   print(table.current_page, "of", table.page_count)

Editing
~~~~~~~

Enable the built-in add/edit/delete UI with ``allow_add`` / ``allow_edit`` /
``allow_delete`` — they open form dialogs and persist to the data source. Mutate
programmatically with ``insert_rows`` / ``update_rows`` / ``delete_rows``, and
react with the row events:

.. code-block:: python

   table = bs.Table(
       columns=cols, rows=people,
       allow_add=True, allow_edit=True, allow_delete=True,
   )

   table.insert_rows([{"name": "New Hire", "role": "Intern"}])
   table.update_rows([{"id": 3, "role": "Lead"}])   # each dict needs an id
   table.delete_rows([7])                            # by id or record dict

   table.on_row_insert(lambda e: print("added",   e.records))
   table.on_row_update(lambda e: print("changed", e.records))
   table.on_row_delete(lambda e: print("removed", e.records))

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

.. image:: /_static/examples/table-edit-light.png
   :class: bs-screenshot-light
   :alt: Table edit record dialog — light theme

.. image:: /_static/examples/table-edit-dark.png
   :class: bs-screenshot-dark
   :alt: Table edit record dialog — dark theme

Row events
~~~~~~~~~~

Row interactions deliver a ``RowEvent`` with the row's ``record`` dict and its
``id``. As with every widget, an ``on_*`` method returns a ``Subscription`` when
given a handler, or a ``Stream`` when called without one:

.. code-block:: python

   table.on_row_click(lambda e: print(e.record, e.id))
   table.on_row_double_click(lambda e: open_detail(e.record))

   sub = table.on_row_right_click(lambda e: ...)
   sub.cancel()     # unsubscribe

Exporting
~~~~~~~~~

``allow_export=True`` adds an export menu with **Copy to clipboard** and **Save to
file** (CSV, plus Excel when the optional ``bootstack[excel]`` extra is installed).
The actions export the selected rows if any are selected, otherwise the whole
filtered set.

.. image:: /_static/examples/table-export-light.png
   :class: bs-screenshot-light
   :alt: Table export menu — light theme

.. image:: /_static/examples/table-export-dark.png
   :class: bs-screenshot-dark
   :alt: Table export menu — dark theme

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

Every export emits an ``Export`` event, and ``scope`` selects what to export
(``"all"``, ``"page"``, or ``"selection"``):

.. code-block:: python

   table.on_export(lambda e: toast(f"Exported {e.count} rows to {e.path}"))
   table.to_csv(scope="selection")

Data binding
~~~~~~~~~~~~

Pass a shared ``SqliteDataSource`` via ``data_source=`` to back the table with a
database or feed it from elsewhere. Mutate the source — even from a background
thread — and the table refreshes itself:

.. code-block:: python

   ds = bs.SqliteDataSource()
   ds.load(people)

   table = bs.Table(columns=cols, data_source=ds)
   ds.insert({"name": "Streamed in"})   # the table updates on its own

See :doc:`../reference/data-sources` for filtering and sorting with ``where()`` /
``order()``, change broadcasting via ``on_change`` / ``observe``, and writing your
own source. ``Table`` requires a ``SqliteDataSource`` specifically.

Appearance
~~~~~~~~~~

Rows are striped by default (``striped=False`` to disable). ``show_status_bar``
governs the footer — the filter/sort/group summary and the pager, which hides on
a single page and collapses when there's nothing to show. ``show_column_chooser``
adds a button that opens a dialog to toggle column visibility:

.. code-block:: python

   bs.Table(columns=cols, rows=people, show_column_chooser=True)

.. image:: /_static/examples/table-column-chooser-light.png
   :class: bs-screenshot-light
   :alt: Table column chooser — light theme

.. image:: /_static/examples/table-column-chooser-dark.png
   :class: bs-screenshot-dark
   :alt: Table column chooser — dark theme

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

.. autoclass:: bootstack.widgets.table.Table
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/table.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
