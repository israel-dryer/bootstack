Theming
=======

Color themes, runtime theme switching, and fonts. Declare a theme in code, switch
the active theme at runtime, look up resolved theme colors, and adjust the
application fonts. These names span two import paths — the two switch verbs are on
the top-level compose surface (``bootstack.set_theme``), the rest live in
``bootstack.style`` — but they are one job, so the reference groups them together.

For task-oriented introductions see the :doc:`/reference/theming` and
:doc:`/reference/typography` guides.

Theme switching
---------------

Switch the active theme at runtime. Part of the top-level compose surface.

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.set_theme
   bootstack.toggle_theme

Themes
------

Declare a color theme in code, install it, and resolve color tokens against the
active theme.

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.style.Theme
   bootstack.style.get_theme
   bootstack.style.get_theme_color
   bootstack.style.get_themes

Fonts
-----

Inspect and adjust the application fonts at runtime.

.. autosummary::
   :toctree: generated
   :nosignatures:

   bootstack.style.get_font_families
   bootstack.style.set_font_family
   bootstack.style.update_font_token

Type aliases
------------

.. currentmodule:: bootstack.style

.. py:type:: ThemeMode

   Theme appearance mode — `'light'` or `'dark'`.
