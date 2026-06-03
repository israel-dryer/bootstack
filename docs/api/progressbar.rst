ProgressBar
===========

A horizontal or vertical progress indicator. Use the determinate mode to show
a fixed fill proportional to a known value, or the indeterminate mode for
operations whose duration is unknown.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/progressbar-light.png"
        alt="ProgressBar demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/progressbar-dark.png"
        alt="ProgressBar demo — dark theme"
        style="max-width:100%;">

Usage
-----

Determinate progress
~~~~~~~~~~~~~~~~~~~~

Set ``value`` between ``0`` and ``max_value`` (default ``100``) to control the
fill level. The bar fills proportionally.

.. code-block:: python

   bs.ProgressBar(value=0)    # empty
   bs.ProgressBar(value=50)   # half full
   bs.ProgressBar(value=100)  # complete

Read or update the value at any time via the ``value`` property:

.. code-block:: python

   bar = bs.ProgressBar(value=0)
   bar.value = 42
   print(bar.value)   # 42.0

Indeterminate mode
~~~~~~~~~~~~~~~~~~

Use ``mode='indeterminate'`` for operations of unknown duration. Call
``start()`` to begin the animation and ``stop()`` to end it.

.. code-block:: python

   bar = bs.ProgressBar(mode="indeterminate")
   bar.start()      # begins looping animation
   # ... do work ...
   bar.stop()

``step(amount)`` advances the fill by ``amount`` (default ``1.0``) when you
want manual control instead of an animation:

.. code-block:: python

   bar = bs.ProgressBar(value=0)
   bar.step(10)   # value → 10
   bar.step(10)   # value → 20

Signal binding
~~~~~~~~~~~~~~

Pass a ``Signal`` to keep the bar in sync with a reactive value:

.. code-block:: python

   progress = bs.Signal(0.0)
   bs.ProgressBar(signal=progress)
   progress.value = 75   # bar updates automatically

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.ProgressBar(value=65, accent="primary")
   bs.ProgressBar(value=65, accent="success")
   bs.ProgressBar(value=65, accent="warning")
   bs.ProgressBar(value=65, accent="danger")

Thin variant
~~~~~~~~~~~~

``variant='thin'`` reduces the bar height for compact layouts or subtle
progress indicators:

.. code-block:: python

   bs.ProgressBar(value=70, accent="primary", variant="thin")

Vertical orientation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.ProgressBar(value=60, orient="vertical")

Custom max value
~~~~~~~~~~~~~~~~

Set ``max_value`` to match your data's natural scale:

.. code-block:: python

   bs.ProgressBar(value=750, max_value=1000, accent="info")

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.progressbar.ProgressBar
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/progressbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
