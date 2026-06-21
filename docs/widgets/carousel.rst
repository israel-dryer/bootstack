Carousel
========

Shows one image slide at a time, with prev/next navigation. `Carousel` is the
focus-on-one counterpart to :doc:`Gallery <gallery>` — it steps through a
collection of image records one slide at a time, with overlaid chevrons, a slide
indicator, an optional caption, transitions, and autoplay.

.. raw:: html

   <video class="bs-video-light" autoplay loop muted playsinline controls
          aria-label="Carousel — slide transitions and navigation">
     <source src="../_static/examples/carousel-video-light.mp4" type="video/mp4">
   </video>
   <video class="bs-video-dark" autoplay loop muted playsinline controls
          aria-label="Carousel — slide transitions and navigation">
     <source src="../_static/examples/carousel-video-dark.mp4" type="video/mp4">
   </video>

Usage
-----

Like a :doc:`Gallery <gallery>`, a carousel is record-native — give it the same
``items=`` or ``data_source=`` records. It pairs naturally with
``Gallery.on_item_activate`` to open a full-size pop-up viewer: a carousel over
the same items, starting at the activated slide.

Slides
~~~~~~

Each record names the image through `image_field` (an :class:`Image
<bootstack.images.Image>`, a file path, or a PIL image) and, optionally, a
caption through `caption_field`:

.. code-block:: python

   items = [
       {"id": 1, "image": "beach.jpg",  "name": "Beach"},
       {"id": 2, "image": "sunset.jpg", "name": "Sunset"},
   ]

   bs.Carousel(items=items, caption_field="name")

`fit` controls how each image scales into the stage — the same modes as
:doc:`Picture <picture>`, defaulting to `'contain'` so the whole image shows.
`corner_radius` rounds the slide.

Navigating
~~~~~~~~~~

Users navigate with the overlaid chevrons, the **arrow keys**, or the indicator
dots. Drive it from code with `next`, `previous`, and `go_to`, and read the
state through `index`, `current`, and `count`:

.. code-block:: python

   carousel = bs.Carousel(items=items)
   carousel.next()
   carousel.go_to(3)
   print(carousel.current)    # the current record dict

`index` is a live property — assign to it to jump to a slide.

Transitions
~~~~~~~~~~~

`transition` animates the change between slides — `'slide'` (default), `'fade'`,
or `'none'`:

.. code-block:: python

   bs.Carousel(items=items, transition="slide")   # default
   bs.Carousel(items=items, transition="fade")

Indicator and arrows
~~~~~~~~~~~~~~~~~~~~

`indicator` selects the slide indicator — `'dots'` (default), `'count'`, or
`'none'`. Set `show_arrows=False` to hide the chevrons:

.. code-block:: python

   bs.Carousel(items=items, indicator="count")
   bs.Carousel(items=items, show_arrows=False, indicator="dots")

With more than eight slides, `'dots'` automatically switches to a
`current / total` counter — a long row of dots is neither readable nor
clickable:

.. image:: /_static/examples/carousel-many-light.png
   :class: bs-screenshot-light
   :alt: Carousel with many slides — count indicator, light theme

.. image:: /_static/examples/carousel-many-dark.png
   :class: bs-screenshot-dark
   :alt: Carousel with many slides — count indicator, dark theme

Autoplay
~~~~~~~~

`autoplay=True` advances the slides on a timer; `interval` sets the dwell time
per slide and `loop` wraps past the ends. Control playback with `play` and
`pause`:

.. code-block:: python

   carousel = bs.Carousel(items=items, autoplay=True, interval=3000)
   carousel.pause()
   carousel.play()

Reacting to changes
~~~~~~~~~~~~~~~~~~~

`on_change` fires when the active slide changes; `on_item_click` fires when the
current slide is clicked — the hook for closing a pop-up viewer or opening a
detail view:

.. code-block:: python

   carousel.on_change(lambda r: print("now showing", r["name"]))
   carousel.on_item_click(lambda r: open_detail(r))

Full-size viewer from a Gallery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common pattern is to let a thumbnail :doc:`Gallery <gallery>` open a larger
view: double-clicking a thumbnail pops up a window with a full-size carousel of
the same photos, starting on the one you picked. There is no special widget for
this — you compose a `Gallery` and a `Carousel`. Because both read the same
records, the only work is finding the activated record's slide position:

.. code-block:: python

   photos = [
       {"id": 1, "image": "beach.jpg",  "name": "Beach"},
       {"id": 2, "image": "sunset.jpg", "name": "Sunset"},
       # ...
   ]

   def open_viewer(record):
       # the record's id is its identity, not its position — find the index
       start = next(i for i, p in enumerate(photos) if p["id"] == record["id"])
       with bs.Window(title=record["name"], size=(900, 650),
                      modal=True, center_on_parent=True) as win:
           viewer = bs.Carousel(items=photos, index=start, grow=True, horizontal="stretch")
           viewer.on_item_click(lambda r: win.close())   # click the photo to close
       win.show()

   gallery = bs.Gallery(items=photos, selection_mode="single")
   gallery.on_item_activate(open_viewer)

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`Gallery <gallery>` — the grid of thumbnails a carousel pairs with.
- :doc:`Picture <picture>` — the single-image display widget.
- :class:`Image <bootstack.images.Image>` — the image source handle.

API
---

The complete reference for :class:`Carousel <bootstack.Carousel>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Carousel

Full Example
------------

.. literalinclude:: ../../docs/examples/carousel.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
