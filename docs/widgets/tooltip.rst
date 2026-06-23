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

A tooltip is an *attachment*, not a placed widget: create it once on a target and
it manages its own hover, show, and hide. Keep a reference only if you want to
update its ``text`` or ``destroy()`` it later. Positioning follows the mouse by
default, or pins to an edge of the target with ``anchor_point``.

Basic
~~~~~

Pass any bootstack widget as the first argument followed by text.
The tooltip appears after 250 ms on hover and hides on mouse leave or click.

.. code-block:: python

   btn = bs.Button("Save")
   bs.Tooltip(btn, "Save your changes to disk")

Covering a container
~~~~~~~~~~~~~~~~~~~~~

When the target is a container, the tooltip shows while the pointer is anywhere
inside it — including over its children. This covers the children that exist
when the tooltip is created.

.. code-block:: python

   with bs.Card(gap=8) as card:
       bs.Label("Disk usage")
       bs.Label("82% full")
   bs.Tooltip(card, "Hover anywhere on the card")

Add children to the container *after* creating the tooltip and they are not
covered automatically. Call ``refresh_bindings()`` to extend coverage to them —
it is safe to call repeatedly.

.. code-block:: python

   tip = bs.Tooltip(card, "Hover anywhere on the card")
   bs.Label("3.2 GB free", parent=card)   # added later
   tip.refresh_bindings()                 # now covered too

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

.. image:: /_static/examples/tooltip-anchor-light.png
   :class: bs-screenshot-light
   :alt: Tooltips anchored above, below, and to the right — light theme

.. image:: /_static/examples/tooltip-anchor-dark.png
   :class: bs-screenshot-dark
   :alt: Tooltips anchored above, below, and to the right — dark theme

Accent colors
~~~~~~~~~~~~~

Color-code tooltips by intent with ``accent=``.

.. code-block:: python

   bs.Tooltip(btn_p, "Primary tooltip", accent="primary")
   bs.Tooltip(btn_s, "Success tooltip", accent="success")
   bs.Tooltip(btn_w, "Warning tooltip", accent="warning")
   bs.Tooltip(btn_d, "Danger tooltip",  accent="danger")

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

Updating the text
~~~~~~~~~~~~~~~~~

``text`` is a live property. Keep a reference to the tooltip and assign a new
value to change it — a visible tooltip updates immediately, and the next hover
shows the new text.

.. code-block:: python

   tip = bs.Tooltip(save_btn, "Not saved")
   # … after saving …
   tip.text = "All changes saved"

Removing a tooltip
~~~~~~~~~~~~~~~~~~

Call ``destroy()`` to remove the tooltip and unbind all event handlers from
the target widget.

.. code-block:: python

   tip = bs.Tooltip(btn, "Temporary help text")
   # … later …
   tip.destroy()

See also
--------

:doc:`contextmenu` — a popup attached to a widget, opened on right-click rather
than hover.

:doc:`toast` — transient corner notifications for status and feedback.

API
---

The complete reference for :class:`Tooltip <bootstack.Tooltip>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Tooltip

Full Example
------------

.. literalinclude:: ../../docs/examples/tooltip.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
