Data Sources
============

A data source is the bridge between your records and the data-bound widgets —
:doc:`/widgets/listview` and :doc:`/widgets/datatable`. It owns the records and
serves them a page at a time, so the same widget works whether your data lives in
memory, a SQLite database, or a file on disk. (:doc:`/widgets/tree` isn't
data-source-backed — it holds its own nodes in memory — but shares the same
record and :ref:`data bag <carrying-extra-data>` model.)

You often don't touch a data source at all — pass ``items=`` / ``rows=`` and the
widget builds one for you. Reach for an explicit source when you want to share
data between widgets, back it with a database, or load it from a file.

In-memory data
--------------

``MemoryDataSource`` holds a list of record dicts. Create it and load rows with
``load()``, then hand it to a widget:

.. code-block:: python

   records = [
       {"name": "Ada", "role": "Engineer"},
       {"name": "Linus", "role": "Maintainer"}
   ]

   ds = bs.MemoryDataSource().load(records)
   bs.ListView(data_source=ds)

SQLite-backed data
------------------

``SqliteDataSource`` keeps rows in an SQLite database (in-memory by default, or
a file path). It is the default source a :class:`DataTable
<bootstack.widgets.datatable.DataTable>` builds when you pass ``rows=`` — or
supply your own to back the table with a database file:

.. code-block:: python

   ds = bs.SqliteDataSource("app.db")
   ds.load(records)
   bs.DataTable(data_source=ds)

File-backed data
----------------

``FileDataSource`` loads records from CSV, TSV, JSON, and JSONL files, configured
with a ``FileSourceConfig``. It reads the file into memory and treats the original
as **read-only input** — edits live in memory only and are not written back, and
``reload()`` re-reads the file. To save changes, export them to a new file
(:meth:`export_csv <bootstack.data.SqliteDataSource.export_csv>` or the
:class:`DataTable <bootstack.widgets.datatable.DataTable>` export menu). Only
``SqliteDataSource`` (file-backed) persists changes in place:

.. code-block:: python

   config = bs.FileSourceConfig(file_format="csv", has_header=True)
   ds = bs.FileDataSource("people.csv", config=config)
   bs.DataTable(data_source=ds)

.. note::

   **Planned:** support for columnar and scientific formats — Parquet, Feather,
   and HDF5 (plus XML) — via optional extras (``pip install bootstack[parquet]``,
   ``bootstack[hdf5]``). Each will be a streaming reader that ingests large files
   in chunks with bounded memory, rather than loading the whole file at once.

.. _carrying-extra-data:

Carrying extra data
-------------------

A record can hold more than the widget shows. The columns of a ``DataTable`` or
the template of a ``ListView`` are a *view* over the record — fields you don't
display are still carried through, and event handlers get the whole record back,
not a stripped-down shadow:

.. code-block:: python

   rows = [
       {"id": 1, "name": "Ada", "role": "Engineer",
        "tags": ["math", "logic"], "profile": {"era": 1840}},
   ]
   table = bs.DataTable(rows=rows, columns=["name", "role"])  # tags/profile hidden

   table.on_row_click(lambda e: print(e.record["tags"]))      # → ['math', 'logic']

This works the same on every source, but *what* a field may hold depends on
where the records live:

- **In-memory** (``MemoryDataSource``, ``FileDataSource``, and the default
  ``ListView`` source) holds **anything**, including live Python objects, by
  reference. The field you put in is the object you get back.
- **SQLite** (``SqliteDataSource``) is persistent. Scalar fields (text, numbers,
  booleans) become real columns you can filter and sort on. Non-scalar fields
  (lists, dicts) are carried as JSON automatically and merged back transparently
  on read — so records still read flat and complete. Because they ride a JSON
  blob, **bagged fields are preserved but not queryable** via ``where`` / ``order``
  (keep anything you need to filter on as a scalar field). Values must be
  JSON-serializable; handing a live object to a SQLite-backed source raises
  :class:`SerializationError <bootstack.errors.SerializationError>` — use an in-memory
  source for those.

Filtering and sorting
---------------------

Build a filter condition with ``bs.col`` and apply it with ``where()``. Sort
with ``order()`` — a leading ``-`` sorts descending. Both return the source, so
they chain, and both behave the same whether the data lives in memory, SQLite,
or a file:

.. code-block:: python

   from bootstack import col

   ds.where(col("age") >= 25)
   ds.where(col("department").is_in(["Sales", "Engineering"]))
   ds.where(col("name").contains("ada"))
   ds.order("-salary", "name")           # salary descending, then name ascending

   ds.where(None)                        # clear the filter
   ds.order()                            # clear the sort

A column supports the comparison operators (``==``, ``!=``, ``<``, ``<=``,
``>``, ``>=``), text matching (``contains``, ``startswith``, ``endswith`` —
case-insensitive), ``is_in(values)``, and ``is_null()`` / ``is_not_null()``.

Combining conditions
~~~~~~~~~~~~~~~~~~~~~

To require several conditions at once, use ``all_of`` (every condition must
hold) or ``any_of`` (at least one). They read top-to-bottom and need no
parentheses:

.. code-block:: python

   from bootstack import col, all_of, any_of

   ds.where(all_of(col("status") == "active", col("name").contains("ada")))
   ds.where(any_of(col("dept") == "Sales", col("dept") == "Engineering"))

For a complex filter, build the pieces as named conditions and pass the result
in — it reads far better than one long expression:

.. code-block:: python

   active = col("status") == "active"
   senior = col("level").is_in(["senior", "staff"])
   ds.where(all_of(active, senior))

The operators ``&`` (and), ``|`` (or), and ``~`` (not) also combine conditions.
They are terser, but mind Python's precedence — ``&`` / ``|`` bind tighter than
the comparisons, so each comparison needs its own parentheses:

.. code-block:: python

   ds.where((col("status") == "active") & (col("age") >= 25))

Conditions never interpolate values into SQL — SQLite binds them as parameters
— so a filter built from user input cannot inject SQL.

.. note::

   The data widgets drive filtering and sorting through their own UI (column
   headers, the search bar, column filters). Call ``where()`` / ``order()``
   yourself when you share a source between widgets or filter programmatically —
   bound widgets refresh automatically (see :ref:`observing-changes`).

.. _observing-changes:

Observing changes
-----------------

A source broadcasts its changes, so a widget bound to one stays in sync without
a manual refresh. Mutate the source directly — even from a background thread —
and any bound ``Table`` or ``ListView`` updates itself:

.. code-block:: python

   ds = bs.MemoryDataSource().load(initial_rows)
   bs.ListView(data_source=ds)

   # Later — from a poll loop, a websocket, any thread:
   ds.insert(new_row)        # the list refreshes on its own

The update is marshaled onto the UI thread for you, and a burst of mutations in
one turn is coalesced into a single refresh.

Use ``on_change`` to react yourself — for example, to drive a dashboard tile
from the row count. With no argument it returns a :class:`Stream
<bootstack.Stream>` you can ``map`` / ``debounce`` and ``listen`` to; with a
handler it subscribes directly and returns a cancellable subscription. The
handler receives a :class:`DataChangeEvent <bootstack.events.DataChangeEvent>`:

.. code-block:: python

   ds.on_change().map(lambda e: ds.count).listen(badge.set_value)

   sub = ds.on_change(lambda e: print("changed:", e.kind))
   sub.cancel()

``observe`` goes a step further: declare a ``where`` / ``order`` query once and
get a live result set — the matching rows now, and a fresh set whenever a
relevant change lands. It is the "observable query" pattern, ideal for a small
derived view or a metric:

.. code-block:: python

   ds.observe(col("status") == "active", "-created").listen(
       lambda rows: gauge.set_value(len(rows))
   )

.. note::

   ``observe`` re-runs the whole query and re-emits the full result set on every
   relevant change, so keep it to *small* derived sets (metrics, a short list, a
   side panel). Large or virtualized views — ``Table``, ``ListView`` — should
   bind to the source directly instead; they already listen via ``on_change``
   and refetch only their visible window.

Writing your own source
-----------------------

Any object that satisfies :class:`DataSourceProtocol
<bootstack.data.DataSourceProtocol>` can back a data widget. The easiest way to
build one is to subclass :class:`BaseDataSource <bootstack.data.BaseDataSource>`,
which supplies the shared paging and utility logic and leaves you to implement
the storage-specific methods (``load``, ``page``, CRUD):

.. code-block:: python

   class ApiDataSource(bs.BaseDataSource):
       def load(self, records): ...
       def page(self, page=None): ...

Records are plain dicts — :data:`Record <bootstack.data.Record>` is
``dict[str, Primitive]``, and :data:`Primitive <bootstack.data.Primitive>` is
the set of values a cell may hold (``str``, ``int``, ``float``, ``bool``,
``None``).

Honoring the data bag
~~~~~~~~~~~~~~~~~~~~~~

The :ref:`data bag <carrying-extra-data>` is a *contract*, not a mechanism, so
participating takes almost nothing:

- Return **complete records** from ``page`` / ``page_slice`` / ``get`` —
  including fields the widget doesn't display. Don't strip anything.
- Declare any bookkeeping keys you add (an internal id, a selection flag) by
  overriding ``_internal_fields()``. The inherited ``_public_record`` /
  ``_record_id`` then hide them and surface ``id`` for you.

That's the whole contract. *How* a field survives is your backend's concern:
an in-memory or document store (e.g. MongoDB's BSON) holds nested values and live
objects natively, so it honors the contract for free. A store with scalar-only
columns has to serialize non-scalar fields itself — that is exactly what
``SqliteDataSource`` does with a hidden JSON column, and why it raises
:class:`SerializationError <bootstack.errors.SerializationError>` for values it
can't serialize. None of that machinery is required of a custom source; only
sources that genuinely serialize need it.

See also
--------

- :doc:`/widgets/listview` — list widget that accepts ``data_source=``.
- :doc:`/widgets/datatable` — data table that accepts any ``data_source=``.

API reference
-------------

The concrete sources:

.. autoclass:: bootstack.data.MemoryDataSource
   :members:

.. autoclass:: bootstack.data.SqliteDataSource
   :members:

.. autoclass:: bootstack.data.FileDataSource
   :members:

.. autoclass:: bootstack.data.FileSourceConfig
   :members:

The interface and base class for writing your own:

.. autoclass:: bootstack.data.DataSourceProtocol
   :members:

.. autoclass:: bootstack.data.BaseDataSource
   :members:
