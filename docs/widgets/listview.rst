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

Extra keys are stored and returned by ``get_selected()`` and events but
are not rendered.

.. code-block:: python

   bs.ListView(items=[
       {
           "id":    1,
           "title": "Alice Johnson",
           "text":  "Engineering lead",
           "icon":  "person-fill",
       },
   ])

Data source
~~~~~~~~~~~

For database or API-backed data, pass a ``DataSourceProtocol`` implementation:

.. code-block:: python

   ds = bs.MemoryDataSource(records)
   bs.ListView(data_source=ds)

Reload after external changes with ``reload()``:

.. code-block:: python

   lv = bs.ListView(data_source=ds)
   ds.insert({"title": "New item"})
   lv.reload()

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

Read the current selection via ``get_selected()``, which returns a list of
the full record dicts:

.. code-block:: python

   lv = bs.ListView(items=records, selection_mode="multi")
   lv.on_selection_changed(lambda e: print(lv.get_selected()))

Clear or fill the selection programmatically:

.. code-block:: python

   lv.select_all()       # multi mode only
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
   lv.on_selection_changed(lambda e: print("selected:", lv.get_selected()))
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

.. autoclass:: bootstack.widgets.listview.ListView
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/listview.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs