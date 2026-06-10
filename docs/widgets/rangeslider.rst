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

Tick marks
~~~~~~~~~~

Use ``tick_step=`` to add major tick marks. ``minor_ticks=`` adds
subdivisions between them.

.. code-block:: python

   bs.RangeSlider(20, 80, tick_step=20)
   bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True)

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
   rs.low_value  = 30     # move low handle
   rs.high_value = 70     # move high handle

Disabled
~~~~~~~~

.. code-block:: python

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
