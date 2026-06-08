Errors
======

Every exception the framework raises inherits from :class:`BootstackError
<bootstack.errors.BootstackError>`, so a single ``except BootstackError``
catches anything bootstack throws while letting ordinary Python errors propagate.
The individual subclasses let you catch one specific failure when you want to
handle it precisely.

.. code-block:: python

   from bootstack.errors import BootstackError

   import bootstack as bs

   try:
       risky_setup()
   except BootstackError as err:
       # any framework error — log it and fall back
       log.warning("bootstack rejected the setup: %s", err)

The errors
----------

``UnknownEventError``
~~~~~~~~~~~~~~~~~~~~~~

Raised by ``widget.on(name, ...)`` when ``name`` isn't an event the widget
supports — almost always a typo. The message lists the widget and the bad name.
Prefer the typed ``on_*()`` shorthands (``on_click``, ``on_change``), which can't
be misspelled; reach for the string form only for dynamic event names:

.. code-block:: python

   from bootstack.errors import UnknownEventError

   try:
       widget.on(event_name, handler)
   except UnknownEventError as err:
       print("no such event:", err)

``ParentResolutionError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when a widget can't find a container to attach to — typically because it
was created outside any ``with`` container block, or under a parent that isn't a
layout container. The fix is structural: create the widget inside an ``App`` or a
layout container (``VStack``, ``HStack``, ``Card``, …):

.. code-block:: python

   with bs.App() as app:
       with bs.VStack():
           bs.Label("Inside a container — fine.")

   bs.Label("Created with no container")   # ParentResolutionError

``DuplicateIdError``
~~~~~~~~~~~~~~~~~~~~~

Raised by a data source when two records share an ``id`` — on ``load()`` of rows
with a colliding id, or on ``insert()`` of a record whose id already exists. Ids
identify rows for selection and events, so they must be unique. It is also raised
if a source is asked to auto-assign an id but the existing ids aren't integers:

.. code-block:: python

   from bootstack.data import MemoryDataSource
   from bootstack.errors import DuplicateIdError

   ds = MemoryDataSource().load([{"id": 1, "name": "Ada"}])

   try:
       ds.insert({"id": 1, "name": "Linus"})   # 1 already exists
   except DuplicateIdError as err:
       print("id clash:", err)

``SerializationError``
~~~~~~~~~~~~~~~~~~~~~~~

Raised when a JSON-backed store is handed a value it can't persist. A
:doc:`Store </reference/store>` and the SQLite/file-backed
:doc:`data sources </reference/data-sources>` keep their values as JSON, so
values must be JSON-serializable (scalars, lists, dicts). To carry a live Python
object, use an in-memory source instead:

.. code-block:: python

   from bootstack.store import Store
   from bootstack.errors import SerializationError

   store = Store("settings")

   try:
       store.set("connection", open("db.sqlite"))   # not JSON-serializable
   except SerializationError as err:
       print("can't persist that:", err)

API reference
-------------

The complete reference for every exception type lives in
:doc:`/api-reference/errors`. At a glance:

.. currentmodule:: bootstack.errors

.. autosummary::
   :nosignatures:

   BootstackError
   DuplicateIdError
   ParentResolutionError
   SerializationError
   UnknownEventError
