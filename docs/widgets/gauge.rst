Gauge
=====

A circular arc gauge for displaying a value within a range. Supports full-circle
and semicircle layouts, solid and segmented arc styles, optional center text with
prefix/suffix formatting, and an interactive drag mode.

.. image:: /_static/examples/gauge-hero-light.png
   :class: bs-screenshot-light
   :alt: Gauge — light theme

.. image:: /_static/examples/gauge-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Gauge — dark theme

Usage
-----

A gauge draws a ``value`` within a ``min_value``/``max_value`` range as a circular
arc, with optional center text. It is a display by default; pass
``interactive=True`` to let the user set the value by dragging the arc.

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

Update the value at runtime via the ``value`` property. ``min_value`` and
``max_value`` are live properties too — assign to them to rescale the gauge as
your data's range changes:

.. code-block:: python

   gauge = bs.Gauge(value=0, max_value=100)
   gauge.value = 65
   gauge.max_value = 2000     # rescale the arc

Labels and formatting
~~~~~~~~~~~~~~~~~~~~~

``subtitle`` appears below the value. ``value_prefix`` and ``value_suffix`` flank
the number. ``value_template`` is a Python format string applied to the raw value.

.. code-block:: python

   bs.Gauge(value=4200, max_value=10000,
            value_prefix="$", value_template="{:.0f}",
            subtitle="Revenue", accent="success")

   bs.Gauge(value=72, value_suffix="%", subtitle="Disk Used", accent="warning")

   bs.Gauge(value=3.7, max_value=5.0, value_template="{:.1f}",
            subtitle="Rating", accent="primary")

Update the subtitle at runtime via the ``subtitle`` property:

.. code-block:: python

   gauge = bs.Gauge(value=50, subtitle="Loading…")
   gauge.subtitle = "Ready"

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
       bs.Gauge(value=65, accent=accent, size=140, thickness=14,
                subtitle=accent.title())

.. image:: /_static/examples/gauge-accents-light.png
   :class: bs-screenshot-light
   :alt: Gauge accent colors — light theme

.. image:: /_static/examples/gauge-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Gauge accent colors — dark theme

Segmented arc
~~~~~~~~~~~~~

Set ``segment_width`` to a positive integer to draw a dashed arc. Smaller values
produce finer dashes:

.. code-block:: python

   bs.Gauge(value=55, subtitle="Solid", accent="primary")           # solid arc
   bs.Gauge(value=55, segment_width=8, subtitle="Segmented",        # coarse segments
            accent="primary")
   bs.Gauge(value=55, segment_width=4, subtitle="Fine segments",    # fine segments
            accent="secondary")

.. image:: /_static/examples/gauge-segments-light.png
   :class: bs-screenshot-light
   :alt: Gauge segmented arc — light theme

.. image:: /_static/examples/gauge-segments-dark.png
   :class: bs-screenshot-dark
   :alt: Gauge segmented arc — dark theme

Arc thickness
~~~~~~~~~~~~~

``thickness`` controls the stroke width in pixels:

.. code-block:: python

   bs.Gauge(value=70, thickness=6,  subtitle="Thin",    accent="info")
   bs.Gauge(value=70, thickness=14, subtitle="Default", accent="info")
   bs.Gauge(value=70, thickness=24, subtitle="Thick",   accent="info")

.. image:: /_static/examples/gauge-thickness-light.png
   :class: bs-screenshot-light
   :alt: Gauge arc thickness — light theme

.. image:: /_static/examples/gauge-thickness-dark.png
   :class: bs-screenshot-dark
   :alt: Gauge arc thickness — dark theme

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

The complete reference for :class:`Gauge <bootstack.Gauge>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Gauge

Full Example
------------

.. literalinclude:: ../../docs/examples/gauge.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs