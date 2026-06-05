Tooltip
=======

A small popup that appears when the mouse hovers over a widget. Tooltips can
follow the mouse or anchor to a specific edge of the target.

.. image:: /_static/examples/tooltip-hero-light.png
   :class: bs-screenshot-light
   :alt: Tooltip — light theme

.. image:: /_static/examples/tooltip-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Tooltip — dark theme

Usage
-----

Basic
~~~~~

Pass any bootstack widget as the first argument followed by text.
The tooltip appears after 250 ms on hover and hides on mouse leave or click.

.. code-block:: python

   btn = bs.Button("Save")
   bs.Tooltip(btn, "Save your changes to disk")

Anchor positioning
~~~~~~~~~~~~~~~~~~

By default the tooltip follows the mouse. Pass ``anchor_point`` to pin the
tooltip to a specific edge of the target widget. ``window_point`` sets which
edge of the tooltip aligns to the anchor — when omitted it defaults to the
opposite of ``anchor_point``.

.. code-block:: python

   btn = bs.Button("More info")

   # Above the button
   bs.Tooltip(btn, "Anchored above", anchor_point="n", window_point="s")

   # Below the button
   bs.Tooltip(btn, "Anchored below", anchor_point="s", window_point="n")

   # To the right
   bs.Tooltip(btn, "Anchored right", anchor_point="e", window_point="w")

Accent colors
~~~~~~~~~~~~~

Color-code tooltips by intent with ``accent=``.

.. code-block:: python

   bs.Tooltip(btn, "Required field", accent="danger")
   bs.Tooltip(btn, "Saved successfully", accent="success")
   bs.Tooltip(btn, "New in this release", accent="info")

.. image:: /_static/examples/tooltip-accents-light.png
   :class: bs-screenshot-light
   :alt: Tooltip accent colors — light theme

.. image:: /_static/examples/tooltip-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Tooltip accent colors — dark theme

Text wrapping and alignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set ``wrap_width`` (pixels) to limit line length. Use ``justify=`` to
control alignment inside the tooltip.

.. code-block:: python

   bs.Tooltip(
       btn,
       "This tooltip has a longer explanation that wraps to multiple lines.",
       wrap_width=220,
   )

   bs.Tooltip(btn, "Centered\ntooltip text", justify="center")

Hover delay
~~~~~~~~~~~

Adjust the delay with ``delay`` (milliseconds). Pass ``0`` for instant
display.

.. code-block:: python

   bs.Tooltip(btn, "Appears instantly", delay=0)
   bs.Tooltip(btn, "Appears after one second", delay=1000)

Auto-flip
~~~~~~~~~

By default (``auto_flip=True``) the tooltip flips axes to stay fully on
screen. Pass ``'vertical'`` or ``'horizontal'`` to restrict flipping to one
axis, or ``False`` to disable it entirely.

.. code-block:: python

   bs.Tooltip(btn, "Never flips", auto_flip=False)
   bs.Tooltip(btn, "Flips vertically only", auto_flip="vertical")

Removing a tooltip
~~~~~~~~~~~~~~~~~~

Call ``destroy()`` to remove the tooltip and unbind all event handlers from
the target widget.

.. code-block:: python

   tip = bs.Tooltip(btn, "Temporary help text")
   # … later …
   tip.destroy()

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.tooltip.Tooltip
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/tooltip.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
