bootstack.style
===============

.. currentmodule:: bootstack.style

Themes, theme switching, and fonts. Declare a color theme in code, switch the
active theme at runtime, look up theme colors, and adjust the application fonts.

For task-oriented introductions see the :doc:`/reference/theming` and
:doc:`/reference/typography` guides.

Themes
------

The declarable color theme. Build one in code and install it.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Theme

Theme control
-------------

Switch and query the active theme, and resolve a color token to a hex value.

.. autosummary::
   :toctree: generated
   :nosignatures:

   set_theme
   toggle_theme
   get_theme
   get_themes
   get_theme_color

Fonts
-----

Inspect and adjust the application fonts at runtime.

.. autosummary::
   :toctree: generated
   :nosignatures:

   get_font_families
   set_font_family
   update_font_token
