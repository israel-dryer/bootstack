Slider
======

A single-handle track for selecting a numeric value within a range.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/slider-hero-light.png"
        alt="Slider demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/slider-hero-dark.png"
        alt="Slider demo — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/slider-accents-light.png"
        alt="Slider accent colors — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/slider-accents-dark.png"
        alt="Slider accent colors — dark theme"
        style="max-width:100%;">

Value badge
~~~~~~~~~~~

Set ``show_value=True`` to display a floating badge with the current value
above the handle.

.. code-block:: python

   bs.Slider(50, show_value=True)

Min / max labels
~~~~~~~~~~~~~~~~

Set ``show_minmax=True`` to display the minimum and maximum values at the
track ends.

.. code-block:: python

   bs.Slider(50, show_minmax=True)

Tick marks
~~~~~~~~~~

Use ``tick_step=`` to add major tick marks. ``minor_ticks=`` adds
subdivisions between them. ``tick_labels=False`` hides the numeric labels.
``tick_format=`` controls how tick and badge labels are formatted.

.. code-block:: python

   bs.Slider(50, tick_step=25)
   bs.Slider(50, tick_step=25, minor_ticks=4)
   bs.Slider(0.5, min_value=0, max_value=1, tick_step=0.25, tick_format="{:.0%}", show_value=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/slider-ticks-light.png"
        alt="Slider tick marks — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/slider-ticks-dark.png"
        alt="Slider tick marks — dark theme"
        style="max-width:100%;">

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[float]`` with ``signal=``. The slider and signal stay in sync.

.. code-block:: python

   volume = bs.Signal(50.0)
   bs.Slider(signal=volume)
   volume.subscribe(lambda v: update_volume(v))

Disabled
~~~~~~~~

.. code-block:: python

   bs.Slider(60, disabled=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/slider-disabled-light.png"
        alt="Slider disabled — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/slider-disabled-dark.png"
        alt="Slider disabled — dark theme"
        style="max-width:100%;">

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`rangeslider` — two-handle range selection
* :doc:`numberfield` — numeric input with typed entry

API
---

.. autoclass:: bootstack.widgets.slider.Slider
   :members:
   :undoc-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/slider.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
