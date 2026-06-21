Slider
======

A single-handle track for selecting a numeric value within a range.

.. image:: /_static/examples/slider-hero-light.png
   :class: bs-screenshot-light
   :alt: Slider demo — light theme

.. image:: /_static/examples/slider-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Slider demo — dark theme

Usage
-----

A slider holds a numeric ``value`` within a ``min_value``/``max_value`` range,
always clamped to the bounds. The decision you make is *when* to react:
``on_change`` fires continuously as the handle moves, while ``on_commit`` fires
once on release — reach for ``on_commit`` when the work per update is expensive.

Basic
~~~~~

.. code-block:: python

   bs.Slider()
   bs.Slider(50, min_value=0, max_value=100)

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Slider(50, accent="primary")
   bs.Slider(50, accent="secondary")
   bs.Slider(50, accent="info")
   bs.Slider(50, accent="success")
   bs.Slider(50, accent="warning")
   bs.Slider(50, accent="danger")

.. image:: /_static/examples/slider-accents-light.png
   :class: bs-screenshot-light
   :alt: Slider accent colors — light theme

.. image:: /_static/examples/slider-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Slider accent colors — dark theme

Value badge
~~~~~~~~~~~

Set ``show_value=True`` to display a floating badge with the current value
above the handle.

.. code-block:: python

   bs.Slider(50, show_value=True)

.. image:: /_static/examples/slider-value-light.png
   :class: bs-screenshot-light
   :alt: Slider value badge — light theme

.. image:: /_static/examples/slider-value-dark.png
   :class: bs-screenshot-dark
   :alt: Slider value badge — dark theme

Min / max labels
~~~~~~~~~~~~~~~~

Set ``show_minmax=True`` to display the minimum and maximum values at the
track ends.

.. code-block:: python

   bs.Slider(50, show_minmax=True)

.. image:: /_static/examples/slider-minmax-light.png
   :class: bs-screenshot-light
   :alt: Slider min/max labels — light theme

.. image:: /_static/examples/slider-minmax-dark.png
   :class: bs-screenshot-dark
   :alt: Slider min/max labels — dark theme

.. note::

   When ``tick_step`` is set with labels, the range ends are already labeled —
   ``show_minmax`` is mainly for a slider without tick marks.

Tick marks
~~~~~~~~~~

Use ``tick_step=`` to add major tick marks. ``minor_ticks=`` adds
subdivisions between them. ``tick_labels=False`` hides the numeric labels.
``tick_format=`` controls how tick and badge labels are formatted.

.. code-block:: python

   bs.Slider(50, tick_step=25)
   bs.Slider(50, tick_step=25, minor_ticks=4)
   bs.Slider(0.5, min_value=0, max_value=1, tick_step=0.25, tick_format="{:.0%}")

.. image:: /_static/examples/slider-ticks-light.png
   :class: bs-screenshot-light
   :alt: Slider tick marks — light theme

.. image:: /_static/examples/slider-ticks-dark.png
   :class: bs-screenshot-dark
   :alt: Slider tick marks — dark theme

.. note::

   ``tick_step`` only *draws* the marks — the value still moves continuously.
   To make the slider snap to those increments, use ``step=`` (see
   `Snapping to steps`_).

Snapping to steps
~~~~~~~~~~~~~~~~~

Set ``step=`` to constrain the value to discrete increments. Click and drag
values snap to the nearest multiple of ``step`` (measured from ``min_value``),
and the arrow keys move by ``step``. It is independent of ``tick_step`` — set
both for a stepped slider with matching marks, or ``step`` alone to snap without
drawing ticks.

.. code-block:: python

   # Only 0, 5, 10, … 100 — with ticks drawn at the same increments
   bs.Slider(50, min_value=0, max_value=100, step=5, tick_step=5)

When the range is not an even multiple of ``step``, the maximum stays reachable.

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[float]`` with ``signal=``. The slider and signal stay in sync.

.. code-block:: python

   volume = bs.Signal(50.0)
   bs.Slider(signal=volume)
   volume.subscribe(lambda v: update_volume(v))

Events
~~~~~~

``on_change`` fires continuously as the handle moves; ``on_commit`` fires once
when the handle is released or moved by keyboard. Reach for ``on_commit`` when
the work behind the slider is expensive — a network call, a recompute, a redraw.

.. code-block:: python

   s = bs.Slider(50, min_value=0, max_value=100)

   # Fires continuously during a drag — keep this cheap
   s.on_change(lambda e: preview(e.value))

   # Fires once, on release or keyboard commit
   s.on_commit(lambda e: apply(e.value))

   # As a Stream
   s.on_change().debounce(150).listen(lambda e: save(e.value))

The handler receives a :class:`~bootstack.events.SliderEvent` (``on_change``)
or :class:`~bootstack.events.SliderCommitEvent` (``on_commit``); ``event.value``
holds the current value.

Keyboard
~~~~~~~~

When focused, the slider responds to the arrow keys (±1, or ±``step`` when
``step`` is set), ``Shift`` + arrow (a larger jump), and ``Home`` / ``End``
(minimum / maximum). Every keyboard change also emits ``on_commit``.

Disabled
~~~~~~~~

.. code-block:: python

   bs.Slider(60)
   bs.Slider(60, disabled=True)

.. image:: /_static/examples/slider-disabled-light.png
   :class: bs-screenshot-light
   :alt: Slider disabled — light theme

.. image:: /_static/examples/slider-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: Slider disabled — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`rangeslider` — two-handle range selection
* :doc:`numberfield` — numeric input with typed entry

API
---

The complete reference for :class:`Slider <bootstack.Slider>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Slider

Full Example
------------

.. literalinclude:: ../../docs/examples/slider.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
