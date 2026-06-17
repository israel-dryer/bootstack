Picture
=======

Displays an image, scaled to fit the space it is given. ``Picture`` is the
display widget for pictures — the counterpart to an :class:`Image
<bootstack.images.Image>`, which is only a source handle. Hand it an image and it
renders the picture into a resizable area with a chosen fit policy, rounded
corners, and — for animated GIF or WebP sources — automatic playback.

.. image:: /_static/examples/picture-hero-light.png
   :class: bs-screenshot-light
   :alt: Picture — light theme

.. image:: /_static/examples/picture-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Picture — dark theme

Usage
-----

Showing an image
~~~~~~~~~~~~~~~~

Pass an :class:`Image <bootstack.images.Image>` handle, or a file path as a
convenience (it is opened for you):

.. code-block:: python

   from bootstack.images import Image

   bs.Picture("logo.png")                 # a path is opened for you
   bs.Picture(Image.open("photo.jpg"))    # or an explicit handle

A ``Picture`` is not a text widget with an image bolted on — it is sizing-aware,
filling the space it is given and re-fitting the picture as that space changes.
Give it a fixed ``width`` and ``height``, or let it fill its container with
``grow=True``.

Fit modes
~~~~~~~~~

``fit`` controls how the picture is scaled into the display area. The vocabulary
follows CSS ``object-fit``:

.. code-block:: python

   bs.Picture(photo, fit="contain", width=150, height=150)   # default
   bs.Picture(photo, fit="cover",   width=150, height=150)
   bs.Picture(photo, fit="fill",    width=150, height=150)

- ``'contain'`` (default) — scale to fit inside, preserving aspect ratio
  (letterboxing any remainder).
- ``'cover'`` — scale to fill, preserving aspect ratio (cropping the overflow).
- ``'fill'`` — stretch to fill, ignoring aspect ratio.
- ``'none'`` — natural size, no scaling.
- ``'scale-down'`` — like ``'contain'``, but never enlarge past natural size.

.. image:: /_static/examples/picture-fit-light.png
   :class: bs-screenshot-light
   :alt: Picture fit modes — light theme

.. image:: /_static/examples/picture-fit-dark.png
   :class: bs-screenshot-dark
   :alt: Picture fit modes — dark theme

``fit`` is a live property — assign to it to re-fit an existing picture. The
``surface`` token sets the letterbox color shown behind a ``'contain'`` picture.

Rounded corners
~~~~~~~~~~~~~~~

``corner_radius`` rounds the corners with an antialiased edge — useful for
avatars and thumbnails:

.. code-block:: python

   bs.Picture(photo, fit="cover", width=150, height=150, corner_radius=0)
   bs.Picture(photo, fit="cover", width=150, height=150, corner_radius=16)
   bs.Picture(photo, fit="cover", width=150, height=150, corner_radius=36)

.. image:: /_static/examples/picture-corners-light.png
   :class: bs-screenshot-light
   :alt: Picture rounded corners — light theme

.. image:: /_static/examples/picture-corners-dark.png
   :class: bs-screenshot-dark
   :alt: Picture rounded corners — dark theme

Animation
~~~~~~~~~

Animated GIF and WebP sources play automatically and loop. Control playback with
``play``, ``pause``, and ``stop``, and read ``is_playing``:

.. code-block:: python

   clip = bs.Picture(Image.open("spinner.gif"))   # autoplay, loops
   clip.pause()
   clip.play()
   clip.stop()                                     # reset to the first frame

   bs.Picture(Image.open("intro.gif"), autoplay=False, loop=False)

Responsive sizing
~~~~~~~~~~~~~~~~~

Without a fixed ``width``/``height``, a ``Picture`` fills its container and
re-fits as the container resizes:

.. code-block:: python

   with bs.Column(grow=True):
       bs.Picture(photo, fit="contain", grow=True, horizontal="stretch")

Reacting to load and errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``on_load`` fires when the image is decoded and displayed, carrying its natural
size and frame count; ``on_error`` fires when a source fails to load:

.. code-block:: python

   pic = bs.Picture("photo.jpg")
   pic.on_load(lambda e: print(f"{e.width}x{e.height}, {e.frames} frame(s)"))
   pic.on_error(lambda e: print("could not load:", e.message))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

- :class:`Image <bootstack.images.Image>` — the source handle a ``Picture``
  displays; build one with :func:`Image.open <bootstack.images.Image.open>`,
  ``from_bytes``, or ``from_pil``.
- :func:`get_icon <bootstack.images.get_icon>` — a theme-aware icon image.
- :doc:`/reference/images` — the images and icons guide.

API
---

The complete reference for :class:`Picture <bootstack.Picture>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Picture

Full Example
------------

.. literalinclude:: ../../docs/examples/picture.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
