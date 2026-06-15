Images and Icons
================

The :mod:`bootstack.images` module is the framework-native way to show pictures
and icons. Everything starts with an :class:`Image <bootstack.images.Image>` — a
lightweight handle that carries image data (or a deferred icon) and is only
rendered when you hand it to a widget. You can build one before an application
exists and share it across widgets.

.. currentmodule:: bootstack.images

Displaying artwork
------------------

Build an :class:`Image` from a file, raw bytes, or an in-memory Pillow image,
then pass it to any widget that accepts ``image=`` — such as
:class:`~bootstack.Label` or :class:`~bootstack.Button`::

    import bootstack as bs
    from bootstack.images import Image

    with bs.App() as app:
        logo = Image.open("assets/logo.png")
        bs.Label(image=logo)
        bs.Label("Profile", image=Image.open("avatar.png"), icon_position="left")
    app.run()

File and byte sources accept the common raster image formats — **PNG**, **JPEG**,
**GIF**, **BMP**, **TIFF**, **WebP**, and **ICO**. (Animated formats load their
first frame; an animated-image widget is a separate feature.)

A handle reports its size without rendering anything::

    logo = Image.open("assets/logo.png")
    print(logo.width, logo.height)

Theme-aware icons
-----------------

:func:`get_icon` creates an icon from a `Bootstrap Icons
<https://icons.getbootstrap.com>`_ name. Give it a theme color token and the
icon re-renders automatically when the theme changes; give it a hex string and
it stays fixed::

    from bootstack.images import get_icon

    # Follows the theme — re-colors on light/dark switch.
    bs.Button("Save", image=get_icon("save", color="primary"))

    # Fixed color, regardless of theme.
    bs.Label(image=get_icon("star-fill", size=24, color="#ffc107"))

``color`` accepts any theme color token (such as ``'foreground'``, ``'primary'``,
or ``'danger'``) or a ``#hex`` value; it defaults to ``'foreground'``, the
standard text color. For a single decorative icon beside text, the widget's own
``icon=`` parameter is simpler — reach for :func:`get_icon` when you want an
:class:`Image` handle you can reuse or recolor explicitly.

Use :func:`list_icons` to discover the available names — for example to build a
picker or validate input::

    from bootstack.images import list_icons

    all_names = list_icons()
    arrows = list_icons(contains="arrow")

Application icons
-----------------

:class:`AppIcon` renders a Bootstrap glyph as an application icon — no icon file
required::

    from bootstack.images import AppIcon

    with bs.App(icon=AppIcon("rocket", background="primary")) as app:
        bs.Label("Ready for launch")
    app.run()

``App`` and ``Window`` both accept ``icon=`` as an icon file path, an
:class:`Image`, or an :class:`AppIcon`.

An app icon renders in one of two shapes:

- a **tile** — the glyph in ``foreground`` on a filled, rounded ``background``
  (the macOS look); or
- **glyph-only** — the glyph alone in the ``background`` (brand) color on a
  transparent field (the typical Windows and Linux look).

By default (``shape="auto"``) the shape follows the platform and the size — a
tile on macOS, and on Windows and Linux glyph-only at the small title-bar sizes
with a tile at taskbar sizes and up — so ``AppIcon("rocket", background="primary")``
looks right everywhere. Pass ``shape="tile"`` or ``shape="glyph"`` to force one.

The runtime ``icon=`` shown here and the **separate** icon embedded in a packaged
build are covered end to end — along with how to pick a glyph and colors that
make a good icon, and the designer (``bootstack appicon``) — in
:doc:`/tasks/application-icons`.

See also
--------

- :doc:`/reference/theming` — color themes and the tokens icons follow.
- :doc:`/widgets/button` and :doc:`/widgets/label` — the widgets that take
  ``image=``.

API reference
-------------

The complete reference for :mod:`bootstack.images` lives in
:doc:`/api-reference/images`. At a glance:

.. autosummary::
   :nosignatures:

   Image
   get_icon
   list_icons
   AppIcon
