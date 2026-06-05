Data Sources
============

A data source is the bridge between your records and the data-bound widgets —
:class:`ListView <bootstack.widgets.listview.ListView>` and :class:`Table
<bootstack.widgets.table.Table>`. It owns the rows and serves them a page at a
time, so the same widget works whether the data lives in a Python list, a
SQLite database, or a file on disk.

For small lists you often don't touch a data source at all — pass ``items=`` /
``rows=`` and the widget builds one for you. Reach for an explicit source when
you want to share data between widgets, back it with a database, or load it from
a file.

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
a file path). :class:`Table <bootstack.widgets.table.Table>` requires this
source — pass ``rows=`` to let the table create one, or supply your own:

.. code-block:: python

   ds = bs.SqliteDataSource("app.db")
   ds.load(records)
   bs.Table(data_source=ds)

File-backed data
----------------

``FileDataSource`` loads records from CSV, JSON, or other formats, configured
with a ``FileSourceConfig``:

.. code-block:: python

   config = bs.FileSourceConfig(file_format="csv", has_header=True)
   ds = bs.FileDataSource("people.csv", config=config)
   bs.Table(data_source=ds)

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
   yourself when you share a source between widgets or filter programmatically;
   call ``widget.reload()`` afterward to refresh the view.

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

See also
--------

- :doc:`/widgets/listview` — list widget that accepts ``data_source=``.
- :doc:`/widgets/table` — table widget (requires ``SqliteDataSource``).

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
