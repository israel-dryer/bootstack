Label
=====

Static text display with optional icon, semantic font tokens, and accent
colors. The display text is the first positional argument.

.. image:: /_static/examples/label-hero-light.png
   :class: bs-screenshot-light
   :alt: Label — light theme

.. image:: /_static/examples/label-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Label — dark theme

Usage
-----

A label is static, display-only text — pass the text as the first argument, then
shape it with a ``font=`` token, an ``icon=``, and an ``accent=`` color. Bind a
:class:`Signal <bootstack.Signal>` with ``textsignal=`` to update it live.

Font tokens
~~~~~~~~~~~

Use the ``font=`` token string to apply semantic typography. Modifiers like
``[bold]``, ``[italic]``, and ``[underline]`` can be chained. For the full
token list and modifier reference see :doc:`/reference/typography`.

.. code-block:: python

   bs.Label("Display",  font="display-xl")
   bs.Label("Heading",  font="heading-lg")
   bs.Label("Body",     font="body")
   bs.Label("Caption",  font="caption")
   bs.Label("Code",     font="code")

   # Modifiers
   bs.Label("Bold",        font="body[bold]")
   bs.Label("Bold Italic", font="heading-md[italic]")

   # Size adjustment relative to base
   bs.Label("Larger",  font="body[+2]")
   bs.Label("Smaller", font="body[-1]")

Accent colors
~~~~~~~~~~~~~

Use ``accent=`` to apply a semantic text color that adapts to the active theme.

.. code-block:: python

   bs.Label("Primary",   accent="primary",   font="body[bold]")
   bs.Label("Secondary", accent="secondary", font="body[bold]")
   bs.Label("Info",      accent="info",      font="body[bold]")
   bs.Label("Success",   accent="success",   font="body[bold]")
   bs.Label("Warning",   accent="warning",   font="body[bold]")
   bs.Label("Danger",    accent="danger",    font="body[bold]")

.. image:: /_static/examples/label-accents-light.png
   :class: bs-screenshot-light
   :alt: Label accent colors — light theme

.. image:: /_static/examples/label-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Label accent colors — dark theme

Icons
~~~~~

Pass a Bootstrap Icons name to ``icon=``. When ``text`` is empty the icon
displays alone. Use ``icon_position=`` to control placement when both are
present.

.. code-block:: python

   bs.Label("Home",     icon="house")
   bs.Label("Settings", icon="gear",      icon_position="right")
   bs.Label("Warning",  icon="exclamation-triangle", accent="warning")

   # Icon-only — auto-detected when text is empty
   bs.Label(icon="heart-fill", accent="danger")

.. image:: /_static/examples/label-icons-light.png
   :class: bs-screenshot-light
   :alt: Label icons — light theme

.. image:: /_static/examples/label-icons-dark.png
   :class: bs-screenshot-dark
   :alt: Label icons — dark theme

Text wrapping
~~~~~~~~~~~~~

Set ``wrap_width=`` (in pixels) to enable multi-line wrapping.

.. code-block:: python

   bs.Label(
       "A longer label that wraps automatically once it exceeds the "
       "specified pixel width.",
       wrap_width=400,
       accent="secondary",
   )

Reactive text
~~~~~~~~~~~~~

Bind a ``Signal[str]`` to ``textsignal=`` so the label updates automatically.

.. code-block:: python

   count      = bs.Signal(0)
   count_text = bs.Signal("Count: 0")
   count.subscribe(lambda v: count_text.set(f"Count: {v}"))

   bs.Label(textsignal=count_text, font="heading-md", accent="primary")
   bs.Button("+1", on_click=lambda: count.set(count() + 1))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`Label <bootstack.Label>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Label

Full Example
------------

.. literalinclude:: ../../docs/examples/label.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs