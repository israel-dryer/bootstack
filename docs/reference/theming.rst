Theming
=======

A theme defines the application's color palette — the text and background colors,
the named accent roles (``primary``, ``success``, ``danger`` …) that widgets draw
with, and the surface colors behind cards, menus, and inputs. bootstack ships
seven light/dark theme pairs, and you can declare your own.

Setting the theme
-----------------

Choose the starting theme through the app settings, then switch at runtime with
``set_theme``:

.. code-block:: python

   import bootstack as bs

   with bs.App(theme="ocean-dark") as app:
       bs.Button("Day mode", on_click=lambda: bs.set_theme("ocean-light"))
   app.run()

``toggle_theme()`` flips between the configured light and dark themes, and
``get_theme()`` returns the name of the active one:

.. code-block:: python

   bs.toggle_theme()
   bs.get_theme()        # "ocean-light"

.. note::

   ``bs.App`` accepts ``theme=`` directly to set the startup theme, and the
   active theme can be read or changed at runtime through ``app.theme``. The
   pair that ``toggle_theme`` switches between comes from the ``light_theme``
   and ``dark_theme`` options (default ``"bootstrap-light"`` and
   ``"bootstrap-dark"``), passed as ``bs.App`` kwargs.

Listing the available themes
----------------------------

``get_themes()`` returns the installed themes as ``{"name", "display_name"}``
dictionaries — ready to populate a theme picker:

.. code-block:: python

   with bs.App() as app:
       themes = bs.get_themes()
       by_label = {t["display_name"]: t["name"] for t in themes}

       choice = bs.Signal(themes[0]["display_name"])
       bs.Select(options=list(by_label), signal=choice)
       choice.subscribe(lambda label: bs.set_theme(by_label[label]))
   app.run()

Reading theme colors
--------------------

``get_theme_color(token)`` resolves a color token to a hex string in the active
theme. Reach for it when you need a theme color for custom drawing:

.. code-block:: python

   bs.get_theme_color("primary")     # a semantic role
   bs.get_theme_color("background")  # the window background
   bs.get_theme_color("blue[200]")   # a step on a shade's spectrum

Tokens come in a few forms:

- **Semantic roles** — ``primary``, ``secondary``, ``info``, ``success``,
  ``warning``, ``danger``. These are what widgets use through ``accent=``.
- **Base colors** — ``foreground``, ``background``, ``white``, ``black``.
- **Shades and their spectrum** — a base hue such as ``blue`` or ``orange``, plus
  50-step tints and shades from ``blue[50]`` (lightest) through ``blue[500]`` (the
  base hue) to ``blue[950]`` (darkest).
- **Surfaces** — container backgrounds: ``content``, ``card``, ``chrome``,
  ``overlay``, and ``input``.

Declaring a custom theme
------------------------

Create a ``Theme`` and ``install()`` it to register it under its name. A theme
describes a small set of base **shades** (named hues) and the **semantic** roles
that point at a step within a shade's spectrum, e.g. ``"orange[400]"``:

.. code-block:: python

   import bootstack as bs

   bs.Theme(
       name="amber-dark",
       display_name="Amber Dark",
       mode="dark",
       base="dark",                  # inherit everything from the dark theme…
       background="#18130a",         # …then override only what differs
       foreground="#f8f9fa",
       shades={"orange": "#fd7e14"},
       semantic={"primary": "orange[400]", "secondary": "yellow[400]"},
   ).install()

   with bs.App(theme="amber-dark") as app:
       bs.Button("Primary", accent="primary")
   app.run()

Setting ``base`` inherits every field from an existing theme — its shades,
semantic roles, surfaces, and mode — so you declare only what changes. ``shades``
and ``semantic`` are merged onto the base entry by entry.

Omit ``base`` to define a self-contained theme. It must then provide
``foreground``, ``background``, and a full set of shades and semantic roles —
every hue a semantic role references has to be present in ``shades``:

.. code-block:: python

   bs.Theme(
       name="mint-light",
       mode="light",
       foreground="#0b3d2e",
       background="#f2fbf7",
       shades={
           "teal": "#00897b", "green": "#2e7d32", "cyan": "#00acc1",
           "yellow": "#fdd835", "red": "#e53935", "gray": "#9e9e9e",
       },
       semantic={
           "primary": "teal[600]", "secondary": "gray[600]", "info": "cyan[600]",
           "success": "green[600]", "warning": "yellow[700]", "danger": "red[600]",
       },
   ).install()

``install()`` registers the theme; activate it with ``set_theme(name)`` or by
passing ``theme=name`` to ``bs.App``. Use ``install(activate=True)`` to do both at
once.

.. tip::

   Custom themes work best in pairs. Providing a light **and** a dark variant lets
   users switch appearance with ``toggle_theme()``. Point the ``light_theme`` and
   ``dark_theme`` options at your two themes to make them the toggle pair — it is
   not required, but recommended:

   .. code-block:: python

      bs.Theme(name="amber-light", mode="light", base="light",
               background="#f7f2e9", semantic={"primary": "orange[600]"}).install()
      bs.Theme(name="amber-dark", mode="dark", base="dark",
               background="#18130a", semantic={"primary": "orange[400]"}).install()

      with bs.App(
          theme="amber-light",
          light_theme="amber-light",
          dark_theme="amber-dark",
      ) as app:
          bs.Button("Toggle", on_click=bs.toggle_theme)
      app.run()

   A light theme typically points its semantic roles at a darker step (e.g.
   ``orange[600]``) for contrast on a light background, and a dark theme at a
   lighter step (e.g. ``orange[400]``).

.. note::

   A theme can be declared and installed at module level, before ``bs.App()``
   exists — its colors are resolved when the theme is activated, not when it is
   created.

To build a theme from data you already have (loaded from a file, say), use
``Theme.from_dict`` with the same keys:

.. code-block:: python

   spec = {
       "name": "amber-dark", "mode": "dark", "base": "dark",
       "background": "#18130a", "semantic": {"primary": "orange[400]"},
   }
   bs.Theme.from_dict(spec).install()

See also
--------

- :doc:`/reference/typography` — font tokens and the ``font=`` syntax.
- :doc:`/widgets/button` — ``accent=`` selects one of a theme's semantic roles.

API reference
-------------

Functions for controlling and reading the active theme, and the ``Theme`` class
for declaring your own.

.. autoclass:: bootstack.style.theme.Theme
   :members:

.. autofunction:: bootstack.style.set_theme
.. autofunction:: bootstack.style.toggle_theme
.. autofunction:: bootstack.style.get_theme
.. autofunction:: bootstack.style.get_themes
.. autofunction:: bootstack.style.get_theme_color