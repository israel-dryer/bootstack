Theming
=======

A theme defines the application's color palette — the text and background colors,
the named accent roles (``primary``, ``success``, ``danger`` …) that widgets draw
with, and the surface colors behind cards, menus, and inputs. bootstack ships ten
light/dark theme pairs, and you can declare your own.

Setting the theme
-----------------

Choose the starting theme through the app settings, then switch at runtime with
``set_theme``:

.. code-block:: python

   import bootstack as bs

   with bs.App(theme="nord-dark") as app:
       bs.Button("Day mode", on_click=lambda: bs.set_theme("nord-light"))
   app.run()

``toggle_theme()`` flips between the configured light and dark themes, and
``get_theme()`` returns the name of the active one:

.. code-block:: python

   from bootstack.style import get_theme

   bs.toggle_theme()
   get_theme()        # "nord-light"

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
       themes = get_themes()
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

   get_theme_color("primary")        # a semantic role
   get_theme_color("background")     # the window background
   get_theme_color("primary[200]")   # a step on the primary ramp

Tokens come in a few forms:

- **Semantic roles** — ``primary``, ``secondary``, ``info``, ``success``,
  ``warning``, ``danger``. These are what widgets use through ``accent=``.
- **Base colors** — ``foreground``, ``background``, ``white``, ``black``.
- **Shades and their spectrum** — every accent role (and the neutral ``gray``)
  expands into a 50-step spectrum, addressed as ``primary[50]`` (lightest)
  through ``primary[500]`` (the declared anchor) to ``primary[950]`` (darkest).
  The shade families are named for their roles — ``gray``, ``primary``,
  ``success``, ``info``, ``warning``, ``danger`` (and ``secondary`` when the
  theme declares a colored secondary).
- **Surfaces** — container backgrounds: ``content``, ``card``, ``chrome``,
  ``raised``, ``overlay``, and ``input``.

Declaring a custom theme
------------------------

A theme is a **family**: declare each semantic accent once — as the ``[500]``
midpoint of its ramp — plus a ``light`` and/or ``dark`` block giving the
``background`` and ``foreground``. ``install()`` generates and registers both the
``<name>-light`` and ``<name>-dark`` variant; the framework picks the right ramp
step per mode (a darker solid on a light background, a brighter one on dark) so
you never hand-write per-mode shades:

.. code-block:: python

   import bootstack as bs
   from bootstack.style import Theme

   Theme(
       name="sunset",
       display_name="Sunset",
       primary="#fd7e14", success="#198754", info="#0dcaf0",
       warning="#ffc107", danger="#dc3545",   # the [500] anchors
       secondary="#9d4edd",                    # optional colored secondary
       neutral="#8c8a93",                      # gray base for borders/muted text
       light=dict(background="#fbf7f2", foreground="#2b2118"),
       dark=dict(background="#211a14", foreground="#f3e9dd"),
   ).install()

   with bs.App(theme="sunset-dark") as app:
       bs.Button("Primary", accent="primary")
   app.run()

Each accent expands into a full 50–950 spectrum from its anchor, and the neutral
gray drives borders, muted text, and the ``secondary`` role when no colored
``secondary`` is given. Surface colors (cards, chrome, inputs) are derived from
the background automatically, preserving its hue.

You only need one of ``light`` / ``dark`` — provide both for a matched pair.
``install(activate=True)`` registers **and** activates the light variant in one
call; pass a variant name to activate that one instead:

.. code-block:: python

   Theme(name="sunset", primary="#fd7e14",
         dark=dict(background="#211a14", foreground="#f3e9dd")
   ).install(activate="sunset-dark")

When the auto-derived surfaces don't suit a particular background — a very dark
chrome band, say — pin them with ``surfaces=`` (a flat dict applies to both
modes; a ``{"light": ..., "dark": ...}`` dict targets one mode):

.. code-block:: python

   Theme(
       name="sunset", primary="#fd7e14",
       light=dict(background="#fbf7f2", foreground="#2b2118"),
       dark=dict(background="#211a14", foreground="#f3e9dd"),
       surfaces={"dark": {"chrome": "#171109"}},
   ).install()

.. note::

   A theme can be declared and installed at module level, before ``bs.App()``
   exists — its colors are resolved when the theme is activated, not when it is
   created.

To build a theme from data you already have (loaded from a file, say), unpack the
mapping into the constructor — ``Theme`` is a plain dataclass, so the keys are
just its fields:

.. code-block:: python

   spec = {
       "name": "sunset",
       "primary": "#fd7e14",
       "dark": {"background": "#211a14", "foreground": "#f3e9dd"},
   }
   Theme(**spec).install()

See also
--------

- :doc:`/reference/typography` — font tokens and the ``font=`` syntax.
- :doc:`/widgets/button` — ``accent=`` selects one of a theme's semantic roles.

API reference
-------------

The complete reference — the :class:`Theme <bootstack.style.Theme>` class and the
theme-control functions — lives in :doc:`/api-reference/theming` (which also covers
the font functions). At a glance:

.. currentmodule:: bootstack.style

.. autosummary::
   :nosignatures:

   Theme
   set_theme
   toggle_theme
   get_theme
   get_themes
   get_theme_color
