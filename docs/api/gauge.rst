Gauge
=====

A circular arc gauge for displaying a value within a range. Supports full-circle
and semicircle layouts, solid and segmented arc styles, optional center text with
prefix/suffix formatting, and an interactive drag mode.

.. code-block:: python

   bs.Gauge(value=72, value_suffix="%", subtitle="CPU", accent="primary")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/gauge-light.png"
        alt="Gauge demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/gauge-dark.png"
        alt="Gauge demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Variants
~~~~~~~~

``'full'`` (default) draws a complete 360° ring. ``'semi'`` draws a half-circle
arc along the bottom, useful for dashboards.

.. code-block:: python

   bs.Gauge(value=68, variant="full", subtitle="Full")
   bs.Gauge(value=68, variant="semi", subtitle="Semi")

Value range
~~~~~~~~~~~

Set ``min_value`` and ``max_value`` to match your data's natural scale:

.. code-block:: python

   bs.Gauge(value=750, min_value=0, max_value=1000, subtitle="Requests/s")

Update the value at runtime via the ``value`` property:

.. code-block:: python

   gauge = bs.Gauge(value=0, max_value=100)
   gauge.value = 65

Labels and formatting
~~~~~~~~~~~~~~~~~~~~~

``subtitle`` appears below the value. ``value_prefix`` and ``value_suffix`` flank
the number. ``value_format`` is a Python format string applied to the raw value.

.. code-block:: python

   bs.Gauge(value=4200, max_value=10000,
            value_prefix="$", value_format="{:.0f}",
            subtitle="Revenue", accent="success")

   bs.Gauge(value=72, value_suffix="%", subtitle="Disk Used", accent="warning")

   bs.Gauge(value=3.7, max_value=5.0, value_format="{:.1f}",
            subtitle="Rating", accent="primary")

Update the subtitle at runtime via the ``subtitle`` property:

.. code-block:: python

   gauge = bs.Gauge(value=50, subtitle="Loading…")
   gauge.subtitle = "Ready"

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Gauge(value=65, accent="primary")
   bs.Gauge(value=65, accent="success")
   bs.Gauge(value=65, accent="warning")
   bs.Gauge(value=65, accent="danger")

Segmented arc
~~~~~~~~~~~~~

Set ``segment_width`` to a positive integer to draw a dashed arc. Smaller values
produce finer dashes:

.. code-block:: python

   bs.Gauge(value=55, segment_width=8,  accent="primary")   # coarse segments
   bs.Gauge(value=55, segment_width=4,  accent="secondary") # fine segments

Arc thickness
~~~~~~~~~~~~~

``thickness`` controls the stroke width in pixels:

.. code-block:: python

   bs.Gauge(value=70, thickness=6,  subtitle="Thin")
   bs.Gauge(value=70, thickness=14, subtitle="Default")
   bs.Gauge(value=70, thickness=24, subtitle="Thick")

Size
~~~~

``size`` sets the diameter in pixels (default ``200``):

.. code-block:: python

   bs.Gauge(value=60, size=120)   # compact
   bs.Gauge(value=60, size=200)   # default
   bs.Gauge(value=60, size=300)   # large

Interactive mode
~~~~~~~~~~~~~~~~

``interactive=True`` lets the user click or drag the arc to change the value.
``step`` controls how much each drag step changes the value:

.. code-block:: python

   bs.Gauge(value=50, interactive=True, step=5, accent="primary")

Listen for changes via ``on_change``:

.. code-block:: python

   gauge = bs.Gauge(value=50, interactive=True)
   gauge.on_change(lambda e: print("value:", gauge.value))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.gauge.Gauge
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/gauge.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
