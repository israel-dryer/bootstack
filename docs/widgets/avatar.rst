Avatar
======

A small identity badge — a person's picture, or their initials on a filled tile
when there's no image. It's a circle by default, with rounded-square and square
options.

.. image:: /_static/examples/avatar-hero-light.png
   :class: bs-screenshot-light
   :alt: Avatar — light theme

.. image:: /_static/examples/avatar-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Avatar — dark theme

Usage
-----

An image fills the avatar's shape edge to edge — scaled to *cover* it and the
overflow cropped, never letterboxed (the same image pipeline as
:doc:`Picture <picture>`).

From an image
~~~~~~~~~~~~~

Pass an :class:`Image <bootstack.images.Image>` handle, a file path, or a PIL
image:

.. code-block:: python

   bs.Avatar("alice.jpg", size=48)
   bs.Avatar(Image.open("bob.png"), size=64, shape="rounded")

From initials
~~~~~~~~~~~~~

With no image, the avatar shows initials on a `background` tile. Give a `name`
to derive them (first and last initial), or pass `initials` directly:

.. code-block:: python

   bs.Avatar(name="Ada Lovelace")            # -> "AL"
   bs.Avatar(name="Grace Hopper", background="info")
   bs.Avatar(initials="JD", background="success")

If an `image` is given but fails to load, the avatar falls back to initials (or a
plain `background` tile) automatically.

Shape and size
~~~~~~~~~~~~~~

`size` sets the square's edge in pixels; `shape` is `'circle'` (default),
`'rounded'`, or `'square'`:

.. code-block:: python

   bs.Avatar(photo, size=72, shape="circle")
   bs.Avatar(photo, size=72, shape="rounded")
   bs.Avatar(photo, size=72, shape="square")

.. image:: /_static/examples/avatar-shapes-light.png
   :class: bs-screenshot-light
   :alt: Avatar shapes — light theme

.. image:: /_static/examples/avatar-shapes-dark.png
   :class: bs-screenshot-dark
   :alt: Avatar shapes — dark theme

Colors and clicks
~~~~~~~~~~~~~~~~~

`background` colors the initials tile (and the fallback), `foreground` the
initials text — both take a theme color token or a hex string. `on_click` makes
the avatar an entry point (open a profile, a menu, …):

.. code-block:: python

   avatar = bs.Avatar(name="Ada Lovelace", background="primary", foreground="white")
   avatar.on_click(lambda e: open_profile())

Swap the picture at runtime through the `image` property, or update the initials
with `set_initials`.

See also
--------

- :doc:`Picture <picture>` — the general image-display widget.
- :class:`Image <bootstack.images.Image>` — the image source handle.

API
---

The complete reference for :class:`Avatar <bootstack.Avatar>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Avatar

Full Example
------------

.. literalinclude:: ../../docs/examples/avatar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
