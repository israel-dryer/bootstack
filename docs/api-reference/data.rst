bootstack.data
==============

.. currentmodule:: bootstack.data

Data sources and the ``col`` filter language. A data source owns a set of records
and serves them a page at a time, so a data-bound widget works the same whether
the records live in memory, a SQLite database, or a file on disk.

For a task-oriented introduction — when to reach for each source, the data bag,
observing changes, exporting — see the :doc:`/reference/data-sources` guide.

Data sources
------------

The concrete sources, the file-source config object, and the base class and
protocol for writing your own.

.. autosummary::
   :toctree: generated
   :nosignatures:

   MemoryDataSource
   SqliteDataSource
   FileDataSource
   FileSourceConfig
   BaseDataSource
   DataSourceProtocol

Query language
--------------

The ``col`` expression API for building filter conditions and sort keys, free of
SQL. Pass conditions to a source's ``where()`` and sort keys to ``order()``.

.. autosummary::
   :toctree: generated
   :nosignatures:

   col
   Column
   Condition
   SortKey
   any_of
   all_of

Type aliases
------------

The record and cell types shared across the module.

.. autosummary::
   :toctree: generated

   Record
   Primitive

Readers and writers
-------------------

The pluggable format registries behind ``FileDataSource`` and a source's
``save()``. Register a reader or writer to teach the framework a new file format.

.. autosummary::
   :toctree: generated
   :nosignatures:

   read_records
   write_records
   get_reader
   get_writer
   register_reader
   register_writer
   supported_read_extensions
   supported_write_extensions