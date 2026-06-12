Application Icons
=================

An application icon identifies your app wherever the operating system shows it:
the title bar, the taskbar, the task switcher, and — once you package the app —
the file manager, the Start menu or Dock, and pinned shortcuts. bootstack lets
you set it from a single Bootstrap glyph, with no image editor required.

There are **two** icons to think about, for two different moments in your app's
life, and they are set independently.

Two icons, two moments
----------------------

.. list-table::
   :header-rows: 1
   :widths: 18 41 41

   * -
     - Runtime icon
     - Distribution icon
   * - Set with
     - ``App(icon=...)`` / ``Window(icon=...)`` in your code
     - ``[build.icon]`` in ``bootstack.toml`` (embedded by the packager)
   * - Appears on
     - The title bar and taskbar button of the *running* window
     - The packaged file in Explorer, the Start-menu / Dock entry, a pinned
       shortcut, and the taskbar button *before* your window paints its own icon
   * - Form
     - Generated on the fly — no file to manage
     - A real icon **file** embedded in the executable at build time
   * - Colors
     - Theme tokens *or* hex (a theme is active, so tokens resolve)
     - **Hex only** — no app runs during a build to resolve a token

Setting one does not set the other. For a consistent look everywhere, give both
the **same artwork** — the simplest way is to build it once and point both at it.

The runtime icon
----------------

:class:`~bootstack.images.AppIcon` renders a `Bootstrap Icons
<https://icons.getbootstrap.com>`_ glyph into an application icon with no file
required. Pass it as the ``icon=`` of an :class:`~bootstack.App` or
:class:`~bootstack.Window`:

.. code-block:: python

   import bootstack as bs
   from bootstack.images import AppIcon

   launcher = AppIcon("rocket", background="primary", foreground="white")

   with bs.App(title="Launcher", icon=launcher) as app:
       bs.Label("Ready for liftoff.")
   app.run()

``icon=`` also accepts a path to an existing icon file or an
:class:`~bootstack.images.Image`. Colors may be theme color tokens (such as
``"primary"``) or hex strings; a token is resolved once, when the icon is
generated, so the icon does not follow later theme changes.

Shape, and how it adapts to size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An app icon takes one of two shapes:

- a **tile** — the glyph in ``foreground`` on a filled, rounded ``background``
  (the macOS look); or
- **glyph-only** — the glyph alone in the ``background`` (brand) color on a
  transparent field (the classic Windows and Linux look).

With the default ``shape="auto"``, bootstack chooses per platform *and* per
size. macOS icons are always a tile. On Windows and Linux, a single
multi-resolution icon is **glyph-only at the small title-bar sizes** — a bare
mark reads more clearly when there are only a handful of pixels — and a **tile
from taskbar size up**, so it stands out as a branded mark among the other
taskbar icons. Pass ``shape="tile"`` or ``shape="glyph"`` to force one shape at
every size. ``radius`` sets the tile's corner rounding, from ``0.0`` (square) to
``0.5`` (a circle).

Designing it visually
~~~~~~~~~~~~~~~~~~~~~~~

To experiment without editing code, run the designer:

.. code-block:: console

   $ bootstack appicon

Pick a glyph, choose the background and foreground colors and a corner radius,
and preview the result live at every size. When it looks right, export an icon
file or copy a ready-to-paste ``[build.icon]`` snippet for ``bootstack.toml``.

The distribution icon
---------------------

A packaged executable embeds its icon at build time, so it needs a real file on
disk. There are two ways to provide one.

**Export a file and point at it.** Render your :class:`~bootstack.images.AppIcon`
to a file once with :meth:`~bootstack.images.AppIcon.save`. The format follows
the extension — ``.ico`` (Windows, multi-resolution), ``.icns`` (macOS), or
``.png`` (a single 256-pixel image):

.. code-block:: python

   from bootstack.images import AppIcon

   AppIcon("rocket", background="#0d6efd", foreground="#ffffff").save("assets/app.ico")

.. code-block:: toml

   [build.icon]
   path = "assets/app.ico"

**Or describe the glyph and let the build render it** — handy when you do not
want to keep a generated file in version control:

.. code-block:: toml

   [build.icon]
   glyph = "rocket"
   background = "#0d6efd"
   foreground = "#ffffff"
   radius = 0.22
   shape = "auto"

.. note::

   Build-time colors must be **hex values**. Theme color tokens (like
   ``"primary"``) are resolved against the active theme, which exists only while
   an application is running — not during a build.

If you set neither ``path`` nor ``glyph``, the build falls back to the bundled
bootstack icon.

.. tip::

   Keep the two icons in sync. Either export once and point both ``App(icon=)``
   and ``[build.icon] path`` at the same file, or use the same glyph and hex
   colors in both places.

Choosing a glyph and colors
---------------------------

A generated icon is only as good as the glyph and colors you give it. Not every
glyph or color makes a good app icon — these rules of thumb keep it legible:

- **Pick a simple, bold silhouette.** An app icon is recognized by its shape at
  a glance, often at 16–24 px. Filled glyphs — the ``-fill`` variants such as
  ``heart-fill`` or ``lightning-charge-fill`` — hold up far better than thin
  line glyphs, whose strokes break up when small. Avoid busy or detailed glyphs;
  they turn to mush at small sizes. Browse names with ``bootstack icons`` or
  :func:`~bootstack.images.list_icons`.
- **One idea, centered.** A single clear symbol reads; two marks compete.
- **Maximize contrast.** The glyph must stand out from its background. On a tile
  you control both colors, so contrast is easy — a white or near-white glyph on
  a saturated brand background is a safe default. Glyph-only has no background of
  its own, so the brand color has to read against **both** light and dark title
  bars (an icon file cannot follow the system theme); avoid mid-tones that
  disappear against one or the other.
- **Give the brand color some weight.** Saturated, mid-to-dark colors make a
  confident taskbar mark; very pale colors wash out against light window chrome.

The limits of a generated icon
------------------------------

A generated icon is drawn from a *single* vector glyph and scaled to every size
your app needs. bootstack works hard to keep that crisp: it chooses the shape
per size, supersamples at whole-number ratios, snaps the glyph to the pixel
grid, and bakes the exact DPI sizes the system asks for into the ``.ico``. The
result is sharp across the sizes most apps use.

There is, however, a ceiling. A single drawing scaled *down* can never be quite
as crisp at the very smallest sizes (16–24 px) as artwork drawn **for** that
size. Truly pixel-perfect small icons need a **custom bitmap per size**, with
every edge placed on the pixel grid so nothing lands on a half-pixel and softens
under antialiasing. That is exactly how bootstack's own built-in icon was made —
each small size hand-aligned to the grid.

In practice:

- For most apps, prototypes, and internal tools, a generated
  :class:`~bootstack.images.AppIcon` is an excellent, zero-effort icon. Ship it.
- For a polished product where the 16/24 px icon must be razor-sharp, treat the
  generated icon as your starting point and have a designer draw a per-size,
  grid-aligned ``.ico``. Point ``[build.icon] path`` at that hand-made file (and
  pass the same file to ``App(icon=)`` if you want it at runtime too).

See also
--------

- :doc:`/reference/images` — the images and icons module in full, including
  displaying artwork and theme-aware :func:`~bootstack.images.get_icon`.
- :doc:`/reference/theming` — the color tokens an icon's colors can name.
