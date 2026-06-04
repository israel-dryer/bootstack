Typography
==========

bootstack uses a token-based font system. Every widget that accepts a ``font=``
argument takes a token string. Tokens resolve to named Tk fonts at startup and
update automatically when the theme changes.

Font tokens
-----------

All sizes shown are relative to the base size (11 pt on Windows, 13 pt on
macOS). The actual pixel size varies with DPI scaling.

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Token
     - Approx size
     - Weight
     - Typical use
   * - ``display-xl``
     - base+17
     - bold
     - Hero headings, splash screens
   * - ``display-lg``
     - base+11
     - bold
     - Page titles, large callouts
   * - ``heading-xl``
     - base+7
     - bold
     - Section headings
   * - ``heading-lg``
     - base+4
     - bold
     - Sub-section headings
   * - ``heading-md``
     - base+2
     - bold
     - Card titles, dialog headers
   * - ``heading-sm``
     - base+1
     - bold
     - Group labels, compact headings
   * - ``body-lg``
     - base+1
     - normal
     - Emphasized body text
   * - ``body``
     - base
     - normal
     - Default widget text
   * - ``body-sm``
     - base-1
     - normal
     - Secondary text, hints
   * - ``caption``
     - base-2
     - normal
     - Timestamps, metadata, fine print
   * - ``label``
     - base-2
     - bold
     - Form labels, table headers
   * - ``code``
     - base (mono)
     - normal
     - Code, paths, identifiers
   * - ``hyperlink``
     - base
     - normal
     - Inline links (underlined)

Modifiers
---------

Append bracket modifiers to any token. Multiple modifiers can be chained.
Heading tokens are already bold — adding ``[bold]`` is a no-op.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Modifier
     - Effect
   * - ``[bold]``
     - Bold weight
   * - ``[italic]``
     - Italic slant
   * - ``[underline]``
     - Underlined text
   * - ``[overstrike]``
     - Strikethrough
   * - ``[+N]``
     - Increase size by N points relative to the token base
   * - ``[-N]``
     - Decrease size by N points relative to the token base
   * - ``[N]``
     - Set absolute size to N points
   * - ``[Npx]``
     - Set absolute size to N pixels (negative points in Tk)

.. code-block:: python

   bs.Label("Italic caption",    font="caption[italic]")
   bs.Label("Underlined body",   font="body[underline]")
   bs.Label("Slightly larger",   font="body[+2]")
   bs.Label("Slightly smaller",  font="body[-1]")
   bs.Label("Bold italic body",  font="body[bold][italic]")
   bs.Label("Heading italic",    font="heading-md[italic]")

Size delta
----------

``[+N]`` and ``[-N]`` shift the size relative to the token's own base, not
the global base size. ``body[+2]`` is always 2 pt larger than ``body``,
regardless of theme or DPI scaling.

Use absolute sizes (``[14]``) only when you need a specific measurement
independent of the token scale — for example, matching an external design spec.

Custom font families
--------------------

The ``Font`` class resolves any token string to a live Tk font object. Pass it
directly to widgets that accept a raw ``font=`` argument, or use it for
measurement:

.. code-block:: python

   import bootstack as bs

   f = bs.Font("heading-lg[italic]")
   width = f.measure("Hello, world")

See also
--------

:doc:`/reference/theming` — ``Font`` class API reference.

:class:`Label <bootstack.widgets.label.Label>` — the primary widget for
displaying text with font tokens.