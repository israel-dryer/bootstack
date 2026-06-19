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

When focused, the slider responds to the arrow keys (±1), ``Shift`` + arrow
(±10), and ``Home`` / ``End`` (minimum / maximum). Every keyboard change also
emits ``on_commit``.

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
