Theme Toggle
============

``ThemeToggle`` is an icon button that switches between the light and dark theme.
It shows a sun in light mode and a moon in dark mode, calls ``toggle_theme`` on
click, and its icon follows the active theme — so it stays correct when the theme
is changed elsewhere too.

.. code-block:: python

   import bootstack as bs

   with bs.App(theme="bootstrap-light") as app:
       bs.ThemeToggle()
   app.run()

It is a plain button — a stateless action whose icon merely reflects the current
theme — so there is no toggle state to keep in sync (just the sun/moon glyph) and
no risk of looping. It takes the button ``variant`` (default ``'ghost'``) and
``density``:

.. code-block:: python

   bs.ThemeToggle(variant="outline", density="compact")

Override the icons with any `Bootstrap Icons <https://icons.getbootstrap.com/>`_
names:

.. code-block:: python

   bs.ThemeToggle(light_icon="brightness-high", dark_icon="moon-stars-fill")

See also
--------

- :doc:`/reference/theming` — themes, ``set_theme``, and ``toggle_theme``.
- :doc:`/widgets/button` — the button ``ThemeToggle`` builds on.

API reference
-------------

See :class:`ThemeToggle <bootstack.ThemeToggle>` on the
:doc:`/api-reference/widgets` page.
