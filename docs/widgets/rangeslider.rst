RangeSlider
===========

A two-handle track for selecting a low/high value range.

.. image:: /_static/examples/rangeslider-hero-light.png
   :class: bs-screenshot-light
   :alt: RangeSlider demo — light theme

.. image:: /_static/examples/rangeslider-hero-dark.png
   :class: bs-screenshot-dark
   :alt: RangeSlider demo — dark theme

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80)
   bs.RangeSlider(0, 50, min_value=0, max_value=100)

Show value badges
~~~~~~~~~~~~~~~~~

Set ``show_value=True`` to display floating badges on both handles.

.. code-block:: python

   bs.RangeSlider(20, 80, show_value=True)

.. image:: /_static/examples/rangeslider-value-light.png
   :class: bs-screenshot-light
   :alt: RangeSlider value badges — light theme

.. image:: /_static/examples/rangeslider-value-dark.png
   :class: bs-screenshot-dark
   :alt: RangeSlider value badges — dark theme

Tick marks
~~~~~~~~~~

Use ``tick_step=`` to add major tick marks. ``minor_ticks=`` adds
subdivisions between them.

.. code-block:: python

   bs.RangeSlider(20, 80, tick_step=20)
   bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4)

.. image:: /_static/examples/rangeslider-ticks-light.png
   :class: bs-screenshot-light
   :alt: RangeSlider tick marks — light theme

.. image:: /_static/examples/rangeslider-ticks-dark.png
   :class: bs-screenshot-dark
   :alt: RangeSlider tick marks — dark theme

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80, accent="primary")
   bs.RangeSlider(20, 80, accent="secondary")
   bs.RangeSlider(20, 80, accent="info")
   bs.RangeSlider(20, 80, accent="success")
   bs.RangeSlider(20, 80, accent="warning")
   bs.RangeSlider(20, 80, accent="danger")

.. image:: /_static/examples/rangeslider-accents-light.png
   :class: bs-screenshot-light
   :alt: RangeSlider accent colors — light theme

.. image:: /_static/examples/rangeslider-accents-dark.png
   :class: bs-screenshot-dark
   :alt: RangeSlider accent colors — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind ``Signal[float]`` instances to each handle independently.

.. code-block:: python

   lo = bs.Signal(25.0)
   hi = bs.Signal(75.0)
   bs.RangeSlider(low_signal=lo, high_signal=hi)
   lo.subscribe(lambda v: print(f"Low: {v}"))
   hi.subscribe(lambda v: print(f"High: {v}"))

Reading the range
~~~~~~~~~~~~~~~~~

Access both handles at once via ``.value``, or individually via
``.low_value`` and ``.high_value``.

.. code-block:: python

   rs = bs.RangeSlider(20, 80)
   lo, hi = rs.value      # → (20.0, 80.0)
   rs.low_value  = 30     # move low handle (clamped to [min, high])
   rs.high_value = 70     # move high handle (clamped to [low, max])

Events
~~~~~~

``on_change`` fires continuously as either handle moves; ``on_commit`` fires
once when a handle is released or moved by keyboard. Reach for ``on_commit``
when the work behind the slider is expensive — a query, a recompute, a redraw.

.. code-block:: python

   rs = bs.RangeSlider(20, 80, min_value=0, max_value=100)

   # Fires continuously during a drag — keep this cheap
   rs.on_change(lambda e: preview(e.low_value, e.high_value))

   # Fires once, on release or keyboard commit
   rs.on_commit(lambda e: filter_results(e.low_value, e.high_value))

   # As a Stream
   rs.on_change().debounce(150).listen(lambda e: save(e.low_value, e.high_value))

The handler receives a :class:`~bootstack.events.RangeSliderEvent`
(``on_change``) or :class:`~bootstack.events.RangeSliderCommitEvent`
(``on_commit``); ``event.low_value`` and ``event.high_value`` hold the current
handle values.

Keyboard
~~~~~~~~

When focused, ``Tab`` switches between the low and high handle. The active
handle responds to the arrow keys (±1), ``Shift`` + arrow (±10), and ``Home`` /
``End`` (minimum / maximum). Every keyboard change also emits ``on_commit``.

Disabled
~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80)
   bs.RangeSlider(20, 80, disabled=True)

.. image:: /_static/examples/rangeslider-disabled-light.png
   :class: bs-screenshot-light
   :alt: RangeSlider disabled — light theme

.. image:: /_static/examples/rangeslider-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: RangeSlider disabled — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`slider` — single-handle slider
* :doc:`numberfield` — numeric input with typed entry

API
---

The complete reference for :class:`RangeSlider <bootstack.RangeSlider>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.RangeSlider

Full Example
------------

.. literalinclude:: ../../docs/examples/rangeslider.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
