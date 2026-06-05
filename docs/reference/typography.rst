Typography
==========

bootstack uses a token-based font system. Every widget that accepts a ``font=``
argument takes a token string such as ``"body"`` or ``"heading-lg"``. Tokens
resolve to named fonts at startup and update automatically when the theme
changes, so you style text by role rather than by hard-coding families and
sizes. A small set of functions adjusts those tokens at runtime.

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

Setting the application font family
-----------------------------------

``set_font_family`` switches every text token to one family in a single call.
The monospace ``code`` token keeps its own family so code stays readable; pass
``mono_family=`` to change it too:

.. code-block:: python

   import bootstack as bs

   with bs.App() as app:
       bs.set_font_family("Inter")                       # body, headings, labels…
       bs.set_font_family("Inter", mono_family="Fira Code")
   app.run()

If the requested family is not installed, a warning is issued and the current
fonts are left unchanged — text never silently falls back to an unexpected face.

Adjusting a font token
----------------------

``update_font_token`` overrides individual attributes of a single token.
Only the attributes you pass change; the rest are left as is. The update
applies everywhere the token is used:

.. code-block:: python

   bs.update_font_token("body", size=12)              # larger default text
   bs.update_font_token("code", family="JetBrains Mono")
   bs.update_font_token("caption", slant="italic")

Listing installed families
---------------------------

``get_font_families`` returns the installed UI families, sorted and filtered of
system and emoji fonts — ready to populate a font picker or to validate input
before calling ``set_font_family``:

.. code-block:: python

   with bs.App() as app:
       families = bs.get_font_families()
       bs.Select(options=families, signal=bs.Signal(families[0]))
   app.run()

Choosing a font interactively
-----------------------------

``ask_font`` opens a font selector and returns the user's choice as a
``FontChoice`` — a plain namedtuple with ``family``, ``size``, ``weight``,
``slant``, ``underline``, and ``overstrike`` fields (or ``None`` if canceled):

.. code-block:: python

   choice = bs.ask_font(default_font="body")
   if choice:
       bs.update_font_token("body", family=choice.family, size=choice.size)

See also
--------

- :doc:`/reference/theming` — colors, accents, and custom themes.
- :doc:`/widgets/font-dialog` — the ``ask_font()`` / ``FontDialog`` selector.
- :class:`Label <bootstack.widgets.label.Label>` — the primary widget for
  displaying text with font tokens.

API reference
-------------

Functions for setting fonts at runtime, plus the ``FontChoice`` result type.

.. autofunction:: bootstack.style.set_font_family
.. autofunction:: bootstack.style.update_font_token
.. autofunction:: bootstack.style.get_font_families

.. autoclass:: bootstack.widgets.dialogs.FontChoice
