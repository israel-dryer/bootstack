Gallery
=======

A scrollable, selectable grid of image thumbnails.

.. image:: /_static/examples/gallery-hero-light.png
   :class: bs-screenshot-light
   :alt: Gallery — light theme

.. image:: /_static/examples/gallery-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Gallery — dark theme

Usage
-----

Gallery recycles its tiles, so it stays efficient over large collections. It is
record-native — populate it with ``items=`` or a ``data_source=`` and read the
chosen tile(s) back through ``.selection``, the same model :doc:`ListView
<listview>`, :doc:`DataTable <datatable>`, and :doc:`Tree <tree>` share.

Populating the grid
~~~~~~~~~~~~~~~~~~~

Each record names the image to show through `image_field` (an :class:`Image
<bootstack.images.Image>`, a file path, or a PIL image) and, optionally, a
caption through `caption_field`. Other keys ride along in the record bag:

.. code-block:: python

   items = [
       {"id": 1, "photo": "beach.jpg",    "name": "Beach"},
       {"id": 2, "photo": "sunset.jpg",   "name": "Sunset"},
       {"id": 3, "photo": "mountain.jpg", "name": "Mountain"},
   ]

   bs.Gallery(items=items, image_field="photo", caption_field="name")

For database- or API-backed data, pass a `data_source=` instead of `items=`.

Reflow and tile size
~~~~~~~~~~~~~~~~~~~~

By default the grid **reflows** to fit the available width — the column count
changes as the window resizes. Set `tile_size` to size the thumbnails, or fix
the column count with `columns=`:

.. code-block:: python

   bs.Gallery(items=items, tile_size=(160, 160))            # auto columns
   bs.Gallery(items=items, columns=4, tile_size=(120, 120))  # fixed 4-up

`fit` controls how each image is scaled into its tile — the same modes as
:doc:`Picture <picture>` (`'cover'` by default), and `corner_radius` rounds the
thumbnails.

Selection
~~~~~~~~~

Set `selection_mode` to `'single'` or `'multi'` to let tiles be selected;
selected tiles show an accent highlight ring. Read the selection — the full
record bag — through `selection`:

.. code-block:: python

   gallery = bs.Gallery(items=items, selection_mode="multi", accent="primary")
   gallery.on_select(lambda e: print(gallery.selection))   # list of record dicts

.. image:: /_static/examples/gallery-selection-light.png
   :class: bs-screenshot-light
   :alt: Gallery selection — light theme

.. image:: /_static/examples/gallery-selection-dark.png
   :class: bs-screenshot-dark
   :alt: Gallery selection — dark theme

In `'single'` mode `selection` is a record `dict` (or `None`); in `'multi'`
mode it is a `list` of record dicts. Drive selection from code with
`select_items`, `deselect_items`, `select_all`, and `clear_selection`.

Clicks and activation
~~~~~~~~~~~~~~~~~~~~~

`on_item_click` fires when a tile is clicked; `on_item_activate` fires on
double-click — the natural place to open a full-size viewer or detail page:

.. code-block:: python

   gallery.on_item_click(lambda r: print("clicked", r["name"]))
   gallery.on_item_activate(lambda r: open_viewer(r))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`Picture <picture>` — the single-image display widget each tile is built
  from.
- :class:`Image <bootstack.images.Image>` — the image source handle.
- :doc:`ListView <listview>` — the single-column record list with the same
  selection model.

API
---

The complete reference for :class:`Gallery <bootstack.Gallery>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Gallery

Full Example
------------

.. literalinclude:: ../../docs/examples/gallery.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
