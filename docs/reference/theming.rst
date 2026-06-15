Theming
=======

A theme defines the application's colors — the text and background, the named
accent roles (``primary``, ``success``, ``danger``, …) that widgets draw with,
and the surfaces behind cards, menus, and inputs. bootstack ships ten color
themes, and you can declare your own.

Theme families and variants
---------------------------

Every theme is a **family** with a light and/or dark **variant**. The variants
are named ``<family>-<mode>`` — ``bootstrap-light``, ``nord-dark``, and so on.

You always activate a *variant*, by its full name. The bare family name is not a
theme you can set:

.. code-block:: python

   bs.set_theme("nord-dark")    # ok — a variant
   bs.set_theme("nord")         # ThemeError — a family, not a variant

The ten built-ins are families — ``bootstrap``, ``pydata``, ``nord``,
``solarized``, ``catppuccin``, ``gruvbox``, ``dracula``, ``tokyo-night``,
``one``, ``everforest`` — and the themes you declare or derive follow the same
rule. A family needs at least one mode, but not both: a light-only family
registers just ``<family>-light``.

Setting the theme
-----------------

Set the starting theme with ``bs.App(theme=)``, and switch at runtime with
``set_theme``:

.. code-block:: python

   import bootstack as bs

   with bs.App(theme="nord-dark") as app:
       bs.Button("Day mode", on_click=lambda: bs.set_theme("nord-light"))
   app.run()

``toggle_theme()`` flips between the configured light and dark variants, and
``get_theme()`` returns the active one's name:

.. code-block:: python

   from bootstack.style import get_theme

   bs.toggle_theme()
   get_theme()        # "nord-light"

The pair ``toggle_theme`` switches between comes from the ``light_theme`` and
``dark_theme`` app options (default ``"bootstrap-light"`` and
``"bootstrap-dark"``). Read or change the active theme at runtime through
``app.theme``.

Listing the available themes
----------------------------

``get_themes()`` returns the installed themes as ``{"name", "display_name"}``
dictionaries — ready to populate a picker:

.. code-block:: python

   from bootstack.style import get_themes

   with bs.App() as app:
       by_label = {t["display_name"]: t["name"] for t in get_themes()}

       choice = bs.Signal(next(iter(by_label)))
       bs.Select(options=list(by_label), signal=choice)
       choice.subscribe(lambda label: bs.set_theme(by_label[label]))
   app.run()

Color tokens
------------

Widgets pull their colors from named **tokens**. ``get_theme_color(token)``
resolves one to a hex string in the active theme — reach for it when you draw
something custom:

.. code-block:: python

   from bootstack.style import get_theme_color

   get_theme_color("primary")        # a semantic role
   get_theme_color("background")     # the window background
   get_theme_color("primary[200]")   # a step on the primary ramp

Tokens come in a few forms:

- **Semantic roles** — ``primary``, ``secondary``, ``info``, ``success``,
  ``warning``, ``danger``. These are what ``accent=`` selects on a widget.
- **Base colors** — ``foreground``, ``background``, ``white``, ``black``.
- **Shades** — every accent role (and the neutral ``gray``) expands into a
  50-step spectrum, addressed ``primary[50]`` (lightest) through ``primary[500]``
  (the anchor) to ``primary[950]`` (darkest).
- **Surfaces** — container backgrounds: ``content``, ``card``, ``chrome``,
  ``raised``, ``overlay``, ``input``.

Declaring a custom theme
------------------------

Declare a family by giving each semantic accent its anchor — the ``[500]``
midpoint of the ramp — plus a ``light`` and/or ``dark`` block for the background
and foreground. ``install()`` generates and registers both variants:

.. code-block:: python

   from bootstack.style import Theme

   Theme(
       name="sunset",
       display_name="Sunset",
       primary="#fd7e14", success="#198754", info="#0dcaf0",
       warning="#ffc107", danger="#dc3545",   # the [500] anchors
       secondary="#9d4edd",                    # optional colored secondary
       neutral="#8c8a93",                      # gray base for borders and muted text
       light=dict(background="#fbf7f2", foreground="#2b2118"),
       dark=dict(background="#211a14", foreground="#f3e9dd"),
   ).install()

   with bs.App(theme="sunset-dark") as app:
       bs.Button("Primary", accent="primary")
   app.run()

You declare those colors once; the framework derives the rest:

- Each accent **anchor** expands into its full 50–950 ramp, and the framework
  picks the step per mode — a darker solid on light, a brighter one on dark.
- The **neutral** gray drives borders, muted text, and the ``secondary`` role
  when no colored ``secondary`` is given.
- **Surfaces** (cards, chrome, inputs) are derived from the background, keeping
  its hue.

``install(activate=True)`` registers and activates the light variant in one call;
pass a variant name to activate a specific one:

.. code-block:: python

   Theme(name="sunset", primary="#fd7e14",
         dark=dict(background="#211a14", foreground="#f3e9dd"),
   ).install(activate="sunset-dark")

When an auto-derived surface doesn't suit a background — a very dark chrome band,
say — pin it with ``surfaces=``. A flat dict applies to both modes; a
``{"light": …, "dark": …}`` dict targets one:

.. code-block:: python

   Theme(
       name="sunset", primary="#fd7e14",
       light=dict(background="#fbf7f2", foreground="#2b2118"),
       dark=dict(background="#211a14", foreground="#f3e9dd"),
       surfaces={"dark": {"chrome": "#171109"}},
   ).install()

``Theme`` is a plain dataclass, so you can build one from a mapping you already
have — loaded from a file, say — by unpacking it:

.. code-block:: python

   spec = {"name": "sunset", "primary": "#fd7e14",
           "dark": {"background": "#211a14", "foreground": "#f3e9dd"}}
   Theme(**spec).install()

.. note::

   Declare and install at module level, before ``bs.App()`` exists — a theme's
   colors are resolved when it is activated, not when it is created.

Deriving from an existing theme
-------------------------------

To brand an existing family without redeclaring every color, use
:meth:`Theme.from_existing <bootstack.style.Theme.from_existing>`. It copies a
base family and replaces only the tokens you pass:

.. code-block:: python

   # Bootstrap, but with our brand primary — everything else inherited.
   Theme.from_existing("bootstrap", name="acme", primary="#ff5722").install()

   with bs.App(theme="acme-light") as app:
       bs.Button("Primary", accent="primary")
   app.run()

``base`` is a family name (``"bootstrap"``, ``"pydata"``, …) or a ``Theme``;
``name`` is the new family's own name.

The result is a full family, so you can override more than one accent — give it a
new light/dark canvas and surfaces while inheriting the base's accent ramps:

.. code-block:: python

   Theme.from_existing(
       "bootstrap",
       name="midnight",
       light=dict(background="#fafafa", foreground="#1a1a1a"),
       dark=dict(background="#0a0a0a", foreground="#e0e0e0"),
       surfaces={"dark": {"chrome": "#000000"}},
   ).install()   # registers midnight-light and midnight-dark

Whatever you don't override is inherited. An unknown token, or an unknown base
name, raises :class:`ThemeError <bootstack.errors.ThemeError>`.

See also
--------

- :doc:`/reference/typography` — font tokens and the ``font=`` syntax.
- :doc:`/widgets/button` — ``accent=`` selects one of a theme's semantic roles.

API reference
-------------

The complete reference — the :class:`Theme <bootstack.style.Theme>` class and the
theme-control functions — lives in :doc:`/api-reference/theming` (which also
covers the font functions). At a glance:

.. currentmodule:: bootstack.style

.. autosummary::
   :nosignatures:

   Theme
   set_theme
   toggle_theme
   get_theme
   get_themes
   get_theme_color