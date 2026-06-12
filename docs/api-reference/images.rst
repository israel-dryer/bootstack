Images
======

.. currentmodule:: bootstack.images

Toolkit-free image handles and icons. An ``Image`` holds artwork or a deferred
icon and is rendered only when bound to a widget; ``get_icon`` builds a
theme-aware icon from a Bootstrap Icons name; ``AppIcon`` generates an
application icon for ``App`` or ``Window``.

For a task-oriented introduction — displaying artwork, theming icons, and
generating app icons (including for PyInstaller builds) — see the
:doc:`/reference/images` guide.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Image
   get_icon
   list_icons
   AppIcon
