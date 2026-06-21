Button
======

A clickable action trigger. Accepts the button text as the first positional
argument.

.. image:: /_static/examples/button-hero-light.png
   :class: bs-screenshot-light
   :alt: Button — light theme

.. image:: /_static/examples/button-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Button — dark theme

Usage
-----

A button does one thing: it runs an action when activated. Wire that action with
``on_click=`` and shape the rest with two independent knobs — ``accent=`` for
*intent* (the semantic color) and ``variant=`` for *weight* (how much it stands
out). Everything else here is a refinement of those three ideas.

Accent colors
~~~~~~~~~~~~~

Use ``accent=`` to express intent. The button renders correctly across all
themes without hard-coding any color.

.. code-block:: python

   bs.Button("Default")
   bs.Button("Primary",   accent="primary")
   bs.Button("Secondary", accent="secondary")
   bs.Button("Info",      accent="info")
   bs.Button("Success",   accent="success")
   bs.Button("Warning",   accent="warning")
   bs.Button("Danger",    accent="danger")

.. image:: /_static/examples/button-accents-light.png
   :class: bs-screenshot-light
   :alt: Button accent colors — light theme

.. image:: /_static/examples/button-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Button accent colors — dark theme

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight. Useful for distinguishing primary
actions from secondary ones.

.. code-block:: python

   bs.Button("Solid",   accent="primary", variant="solid")
   bs.Button("Outline", accent="primary", variant="outline")
   bs.Button("Ghost",   accent="primary", variant="ghost")

.. image:: /_static/examples/button-variants-light.png
   :class: bs-screenshot-light
   :alt: Button style variants — light theme

.. image:: /_static/examples/button-variants-dark.png
   :class: bs-screenshot-dark
   :alt: Button style variants — dark theme

Icons
~~~~~

Pass any `Bootstrap Icons <https://icons.getbootstrap.com>`_ name to ``icon=``.
The icon appears to the left of the text by default.

.. code-block:: python

   bs.Button("Save",   icon="save")
   bs.Button("Delete", icon="trash",    accent="danger")
   bs.Button("Export", icon="download", accent="secondary", variant="outline")

.. image:: /_static/examples/button-icons-light.png
   :class: bs-screenshot-light
   :alt: Button icons — light theme

.. image:: /_static/examples/button-icons-dark.png
   :class: bs-screenshot-dark
   :alt: Button icons — dark theme

Icon position
~~~~~~~~~~~~~

Use ``icon_position=`` to control where the icon sits relative to the text.
Defaults to ``'left'``.

.. code-block:: python

   bs.Button("Left",   icon="arrow-left",  icon_position="left")
   bs.Button("Right",  icon="arrow-right", icon_position="right")
   bs.Button("Top",    icon="arrow-up",    icon_position="top")
   bs.Button("Bottom", icon="arrow-down",  icon_position="bottom")

.. image:: /_static/examples/button-icon-position-light.png
   :class: bs-screenshot-light
   :alt: Button icon position — light theme

.. image:: /_static/examples/button-icon-position-dark.png
   :class: bs-screenshot-dark
   :alt: Button icon position — dark theme

Icon-only
~~~~~~~~~

Omit the text to show only the icon — ``icon_only`` is inferred
automatically. Pass ``icon_only=True`` explicitly when you want to be
clear about intent.

.. code-block:: python

   # icon_only inferred — no text provided
   bs.Button(icon="plus-lg",  accent="success")
   bs.Button(icon="dash-lg",  accent="danger")
   bs.Button(icon="pencil",   accent="secondary", variant="outline")
   bs.Button(icon="trash",    accent="danger",    variant="outline")

   # explicit form — equivalent, states intent clearly
   bs.Button("Delete", icon="trash", icon_only=True, accent="danger")

.. image:: /_static/examples/button-icon-only-light.png
   :class: bs-screenshot-light
   :alt: Button icon-only — light theme

.. image:: /_static/examples/button-icon-only-dark.png
   :class: bs-screenshot-dark
   :alt: Button icon-only — dark theme

Uniform width
~~~~~~~~~~~~~

Use ``width=`` (in character units) to make a row of buttons the same width.

.. code-block:: python

   bs.Button("Save",   accent="primary", width=10)
   bs.Button("Cancel",                   width=10)
   bs.Button("Reset",  accent="danger",  width=10)

.. image:: /_static/examples/button-width-light.png
   :class: bs-screenshot-light
   :alt: Button uniform width — light theme

.. image:: /_static/examples/button-width-dark.png
   :class: bs-screenshot-dark
   :alt: Button uniform width — dark theme

Compact density
~~~~~~~~~~~~~~~

Use ``density='compact'`` to reduce padding — useful in toolbars where
space is tight.

.. code-block:: python

   bs.Button("Cut",   icon="scissors",  density="compact")
   bs.Button("Copy",  icon="copy",      density="compact")
   bs.Button("Paste", icon="clipboard", density="compact")

.. image:: /_static/examples/button-density-light.png
   :class: bs-screenshot-light
   :alt: Button compact density — light theme

.. image:: /_static/examples/button-density-dark.png
   :class: bs-screenshot-dark
   :alt: Button compact density — dark theme

Disabled state
~~~~~~~~~~~~~~

.. code-block:: python

   bs.Button("Disabled Solid",   accent="primary",                    disabled=True)
   bs.Button("Disabled Outline", accent="primary", variant="outline", disabled=True)

.. image:: /_static/examples/button-disabled-light.png
   :class: bs-screenshot-light
   :alt: Button disabled — light theme

.. image:: /_static/examples/button-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: Button disabled — dark theme

Reactive text
~~~~~~~~~~~~~

Bind a ``Signal[str]`` to ``textsignal=`` so the button text updates
automatically.

.. code-block:: python

   running  = bs.Signal(False)
   btn_text = bs.Signal("Start")

   running.subscribe(lambda v: btn_text.set("Stop" if v else "Start"))

   bs.Button(textsignal=btn_text, accent="primary",
             on_click=lambda: running.set(not running()))

   # Or set directly via the .text property
   btn = bs.Button("Start", accent="primary")
   btn.text = "Stop"

Custom image
~~~~~~~~~~~~

For artwork beyond the Bootstrap Icons set — a logo, an embedded resource —
pass an :class:`Image <bootstack.images.Image>` handle to ``image=``. Reach for
``icon=`` for standard glyphs and ``image=`` for custom pictures.

.. code-block:: python

   from bootstack.images import Image

   bs.Button("Open", image=Image.open("logo.png"))

The handle is also a live property — assigning ``button.image`` swaps the
picture in place. See :doc:`/widgets/picture` and the
:class:`Image <bootstack.images.Image>` reference for the full image API.

Events
~~~~~~

A button fires on **activation** — a mouse release over it, ``Space``/``Return``
while it has keyboard focus, or a programmatic :meth:`click`. A disabled button
never fires on any of those paths. The simplest form is the ``on_click=``
constructor callback, which takes **no arguments**:

.. code-block:: python

   bs.Button("Save",   accent="primary", on_click=handle_save)
   bs.Button("Cancel", on_click=lambda: print("Cancelled"))

Use the ``on_click()`` method when you need a cancellable subscription or want to
compose the event as a :class:`~bootstack.streams.Stream`. Its handler receives
the activation :class:`~bootstack.events.Event`:

.. code-block:: python

   # Cancellable subscription
   btn = bs.Button("Save", accent="primary")
   sub = btn.on_click(lambda event: handle_save())
   sub.cancel()  # unsubscribe

   # Composable Stream — e.g. ignore rapid double-clicks
   btn.on_click().debounce(300).listen(lambda event: handle_save())

.. note::

   Because keyboard and programmatic activations carry no pointer, treat the
   event's position and modifier fields as unset — use ``on_click=`` (or ignore
   the argument) unless you specifically need a mouse-only gesture. See
   :doc:`/tasks/handling-actions` for wiring actions across widgets and
   :doc:`/reference/events` for the full event model.

Keyboard
~~~~~~~~

- **Tab / Shift+Tab** — move focus to or from the button.
- **Space / Return** — activate the focused button, firing the click exactly as a
  mouse release does. A disabled button is skipped in the focus order.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`menubutton` — a button that opens a menu of actions
* :doc:`buttongroup` — a row of related buttons sharing one style
* :doc:`togglebutton` — a button that holds an on/off state
* :doc:`/tasks/handling-actions` — wiring actions and shortcuts across widgets
* :doc:`/reference/events` — the event model behind ``on_click``

API
---

The complete reference for :class:`Button <bootstack.Button>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Button

Full Example
------------

.. literalinclude:: ../../docs/examples/button.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs