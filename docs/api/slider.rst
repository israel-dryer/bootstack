Slider
======

A single-handle track for selecting a numeric value within a range.

.. code-block:: python

   bs.Slider(50, min_value=0, max_value=100)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/slider-light.png"
        alt="Slider demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/slider-dark.png"
        alt="Slider demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

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
   bs.Slider(50, accent="success")
   bs.Slider(50, accent="warning")

Show value badge
~~~~~~~~~~~~~~~~

Set ``show_value=True`` to display a floating badge with the current value
above the handle.

.. code-block:: python

   bs.Slider(50, show_value=True)

Tick marks
~~~~~~~~~~

Use ``tick_step=`` to add major tick marks. ``minor_ticks=`` adds subdivisions.
``tick_labels=False`` hides numeric labels. ``tick_format=`` controls label text.

.. code-block:: python

   bs.Slider(50, tick_step=25)
   bs.Slider(50, tick_step=25, minor_ticks=4)
   bs.Slider(0.5, min_value=0, max_value=1, tick_step=0.25, tick_format="{:.0%}")

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

   bs.Slider(30, disabled=True)

API
---

.. autoclass:: bootstack.widgets.slider.Slider
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/slider.py
   :language: python
   :start-after: import bootstack as bs
