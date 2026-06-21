ListView
========

A virtual-scrolling list for efficiently displaying large datasets. Only
visible rows are rendered, making it suitable for thousands of records.

.. image:: /_static/examples/listview-hero-light.png
   :class: bs-screenshot-light
   :alt: ListView — light theme

.. image:: /_static/examples/listview-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ListView — dark theme

Usage
-----

A list view shows records (each a plain ``dict``) as rows, rendering only the
visible ones so it stays fast over thousands of items. Read or react to the chosen
rows through ``.selection`` and ``on_select``.

Item fields
~~~~~~~~~~~

Each record is a plain ``dict``. The displayed fields are:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Key
     - Description
   * - ``'id'``
     - Unique identifier. Auto-generated if absent.
   * - ``'title'``
     - Primary text, rendered in bold.
   * - ``'text'``
     - Secondary text shown below the title.
   * - ``'icon'``
     - Icon name displayed on the left.
   * - ``'badge'``
     - Short label displayed on the right.

.. code-block:: python

   bs.ListView(items=[
       {
           "id":    1,
           "title": "Alice Johnson",
           "text":  "Engineering lead",
           "icon":  "person-fill",
       },
   ])

Carrying extra data
~~~~~~~~~~~~~~~~~~~~

The keys above are a *view* over the record, not the record itself. Extra keys
are still carried through and handed back — ``selection`` and the item
events return the full record dict, including the undisplayed fields:

.. code-block:: python

   lv = bs.ListView(items=[
       {"id": 1, "title": "Alice", "icon": "person-fill", "tags": ["vip"]},
   ], selection_mode="multi")
   lv.on_item_click(lambda e: print(e["tags"]))   # → ['vip']

The default source is in-memory, so a field can hold any Python object; back the
list with a persistent source and the same storage tiers apply. See
:ref:`carrying-extra-data` for the details.

Data source
~~~~~~~~~~~

For database or API-backed data, pass a ``DataSourceProtocol`` implementation:

.. code-block:: python

   from bootstack.data import MemoryDataSource

   ds = MemoryDataSource().load(records)
   bs.ListView(data_source=ds)

Mutate the source directly — even from a background thread — and the list
refreshes itself, no manual reload needed:

.. code-block:: python

   lv = bs.ListView(data_source=ds)
   ds.insert({"title": "New item"})   # the list updates on its own

See :ref:`observing-changes` for the data source's change broadcasting.

Mutate records at runtime with the CRUD methods:

.. code-block:: python

   lv = bs.ListView(items=[{"id": 1, "title": "Draft"}])
   lv.update_item(1, {"title": "Published"})
   lv.delete_item(1)
   lv.insert_item({"title": "Another"})

Selection
~~~~~~~~~

``selection_mode`` controls how many items can be selected at once.
``show_selection_controls`` adds checkboxes (multi) or radio buttons (single):

.. code-block:: python

   bs.ListView(items=records, selection_mode="single")
   bs.ListView(items=records, selection_mode="multi", show_selection_controls=True)

By default a click selects the row. Pass ``select_on_click=False`` to decouple
the two — a click then activates the row (open it, say) without changing the
selection, which the user drives separately via the checkboxes:

.. code-block:: python

   bs.ListView(items=records, selection_mode="multi",
               show_selection_controls=True, select_on_click=False)

Read the current selection via ``selection``. In ``"multi"`` mode it returns a
list of the full record dicts; in ``"single"`` mode the selected record dict (or
``None``). Non-displayed fields ride along in each record:

.. code-block:: python

   lv = bs.ListView(items=records, selection_mode="multi")
   lv.on_select(lambda e: print(lv.selection))

Set the selection programmatically by record ``id`` — ``select_items`` replaces
the selection in single mode and adds in multi mode; ``deselect_items`` removes:

.. code-block:: python

   lv.select_items([3, 7])   # by record id
   lv.deselect_items([3])
   lv.select_all()           # multi mode only
   lv.clear_selection()

.. image:: /_static/examples/listview-selection-light.png
   :class: bs-screenshot-light
   :alt: ListView multi-select — light theme

.. image:: /_static/examples/listview-selection-dark.png
   :class: bs-screenshot-dark
   :alt: ListView multi-select — dark theme

Row features
~~~~~~~~~~~~

``allow_remove`` adds a × button to each item. ``show_chevron`` adds a
right-pointing chevron, useful for navigation lists. ``allow_reorder``
adds a drag handle so the user can reorder items by dragging:

.. code-block:: python

   bs.ListView(items=records, allow_remove=True)
   bs.ListView(items=records, show_chevron=True)
   bs.ListView(items=records, allow_reorder=True)

.. image:: /_static/examples/listview-features-light.png
   :class: bs-screenshot-light
   :alt: ListView row features — light theme

.. image:: /_static/examples/listview-features-dark.png
   :class: bs-screenshot-dark
   :alt: ListView row features — dark theme

Striped rows and density
~~~~~~~~~~~~~~~~~~~~~~~~

``striped=True`` alternates row backgrounds. ``density='compact'`` reduces
row height:

.. code-block:: python

   bs.ListView(items=records, striped=True)
   bs.ListView(items=records, density="compact")

.. image:: /_static/examples/listview-density-light.png
   :class: bs-screenshot-light
   :alt: ListView striped compact — light theme

.. image:: /_static/examples/listview-density-dark.png
   :class: bs-screenshot-dark
   :alt: ListView striped compact — dark theme

Scrollbar
~~~~~~~~~

The scrollbar is shown by default. Pass ``show_scrollbar=False`` to hide it
(mousewheel scrolling still works):

.. code-block:: python

   bs.ListView(items=records, show_scrollbar=False)

Events
~~~~~~

Item events hand the handler the **record dict** for the affected row directly,
so you read its fields with ``e["field"]`` (plus drag/move metadata such as
``e["id"]`` and ``e["target_index"]``).

All ``on_*`` methods return a ``Subscription`` when called with a handler, or
a ``Stream`` when called without one. Call ``.cancel()`` on the subscription
to unsubscribe:

.. code-block:: python

   lv = bs.ListView(items=records, selection_mode="single")

   sub = lv.on_item_click(lambda e: print("clicked:", e["title"]))
   lv.on_select(lambda e: print("selected:", lv.selection))
   lv.on_item_delete(lambda e: print("deleted:", e["id"]))

   sub.cancel()   # unsubscribe

For reorderable lists, listen for drag completion:

.. code-block:: python

   lv = bs.ListView(items=records, allow_reorder=True)
   lv.on_item_drag_end(lambda e: print("moved to:", e["target_index"]))

Scrolling
~~~~~~~~~

.. code-block:: python

   lv.scroll_to_top()
   lv.scroll_to_bottom()

Accent
~~~~~~

``accent`` colors the selection highlight and drag indicator:

.. code-block:: python

   bs.ListView(items=records, selection_mode="multi", accent="primary")
   bs.ListView(items=records, selection_mode="multi", accent="success")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`ListView <bootstack.ListView>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ListView

Full Example
------------

.. literalinclude:: ../../docs/examples/listview.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs