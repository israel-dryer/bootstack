RangeSlider
===========

A two-handle track for selecting a low/high value range.

.. code-block:: python

   bs.RangeSlider(20, 80)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/rangeslider-light.png"
        alt="RangeSlider demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/rangeslider-dark.png"
        alt="RangeSlider demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80)
   bs.RangeSlider(0, 50, min_value=0, max_value=100)

Show value badges
~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80, show_value=True)

Tick marks
~~~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80, tick_step=20)
   bs.RangeSlider(20, 80, tick_step=20, minor_ticks=4, show_value=True)

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80, accent="success")
   bs.RangeSlider(20, 80, accent="warning")

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
   lo, hi = rs.value          # → (20.0, 80.0)
   rs.low_value  = 30         # move low handle
   rs.high_value = 70         # move high handle

Disabled
~~~~~~~~

.. code-block:: python

   bs.RangeSlider(20, 80, disabled=True)

API
---

.. autoclass:: bootstack.widgets.slider.RangeSlider
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/rangeslider.py
   :language: python
   :start-after: import bootstack as bs
