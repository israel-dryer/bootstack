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
``set_data()``, then hand it to a widget:

.. code-block:: python

   records = [{"name": "Ada", "role": "Engineer"},
              {"name": "Linus", "role": "Maintainer"}]

   ds = bs.MemoryDataSource().set_data(records)
   bs.ListView(data_source=ds)

SQLite-backed data
------------------

``SqliteDataSource`` keeps rows in an SQLite database (in-memory by default, or
a file path). :class:`Table <bootstack.widgets.table.Table>` requires this
source — pass ``rows=`` to let the table create one, or supply your own:

.. code-block:: python

   ds = bs.SqliteDataSource("app.db")
   ds.set_data(records)
   bs.Table(data_source=ds)

File-backed data
----------------

``FileDataSource`` loads records from CSV, JSON, or other formats, configured
with a ``FileSourceConfig``:

.. code-block:: python

   config = bs.FileSourceConfig(file_format="csv", has_header=True)
   ds = bs.FileDataSource("people.csv", config=config)
   bs.Table(data_source=ds)

Writing your own source
-----------------------

Any object that satisfies :class:`DataSourceProtocol
<bootstack.data.DataSourceProtocol>` can back a data widget. The easiest way to
build one is to subclass :class:`BaseDataSource <bootstack.data.BaseDataSource>`,
which supplies the shared paging and utility logic and leaves you to implement
the storage-specific methods (``set_data``, ``get_page``, CRUD):

.. code-block:: python

   class ApiDataSource(bs.BaseDataSource):
       def set_data(self, records): ...
       def get_page(self, page=None): ...

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
