Label
=====

Static text display with optional icon, semantic font tokens, and accent
colors. The display text is the first positional argument.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/label-light.png"
        alt="Label demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/label-dark.png"
        alt="Label demo — dark theme"
        style="max-width:100%;">

Usage
-----

Font tokens
~~~~~~~~~~~

Use the ``font=`` token string to apply semantic typography. Modifiers like
``[bold]``, ``[italic]``, and ``[underline]`` can be chained.

.. code-block:: python

   bs.Label("Display",  font="display-xl")
   bs.Label("Heading",  font="heading-lg")
   bs.Label("Body",     font="body")
   bs.Label("Caption",  font="caption")
   bs.Label("Code",     font="code")

   # Modifiers
   bs.Label("Bold",        font="body[bold]")
   bs.Label("Bold Italic", font="heading-md[bold][italic]")

   # Size adjustment relative to base
   bs.Label("Larger",  font="body+2")
   bs.Label("Smaller", font="body-1")

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

Icons
~~~~~

Pass a Bootstrap Icons name to ``icon=``. When ``text`` is empty the icon
displays alone. Use ``icon_position=`` to control placement when both are
present.

.. code-block:: python

   bs.Label("Home",     icon="house")
   bs.Label("Settings", icon="gear",      icon_position="right")
   bs.Label("Alert",    icon="exclamation-triangle", accent="warning")

   # Icon-only — auto-detected when text is empty
   bs.Label(icon="heart-fill", accent="danger")

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

   bs.Label(textsignal=count_text, font="heading-md[bold]", accent="primary")
   bs.Button("+1", on_click=lambda: count.set(count.get() + 1))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.label.Label
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/label.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
