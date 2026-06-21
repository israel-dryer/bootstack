ProgressBar
===========

A horizontal or vertical progress indicator. Use the determinate mode to show
a fixed fill proportional to a known value, or the indeterminate mode for
operations whose duration is unknown.

.. image:: /_static/examples/progressbar-hero-light.png
   :class: bs-screenshot-light
   :alt: ProgressBar — light theme

.. image:: /_static/examples/progressbar-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ProgressBar — dark theme

Usage
-----

The main decision is ``mode``: **determinate** fill tracks a known ``value``
(``0`` to ``max_value``), while **indeterminate** animates continuously for work
of unknown length. Bind ``value`` to a :class:`Signal <bootstack.Signal>` with
``signal=`` to drive the fill live.

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
   bs.ProgressBar(value=65, accent="secondary")
   bs.ProgressBar(value=65, accent="info")
   bs.ProgressBar(value=65, accent="success")
   bs.ProgressBar(value=65, accent="warning")
   bs.ProgressBar(value=65, accent="danger")

.. image:: /_static/examples/progressbar-accents-light.png
   :class: bs-screenshot-light
   :alt: ProgressBar accent colors — light theme

.. image:: /_static/examples/progressbar-accents-dark.png
   :class: bs-screenshot-dark
   :alt: ProgressBar accent colors — dark theme

Thin variant
~~~~~~~~~~~~

``variant='thin'`` reduces the bar height for compact layouts or subtle
progress indicators:

.. code-block:: python

   bs.ProgressBar(value=40, variant="thin")
   bs.ProgressBar(value=70, accent="primary", variant="thin")
   bs.ProgressBar(value=90, accent="success", variant="thin")

Vertical orientation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.ProgressBar(value=25, orient="vertical")
   bs.ProgressBar(value=50, orient="vertical")
   bs.ProgressBar(value=75, orient="vertical")
   bs.ProgressBar(value=100, orient="vertical")

.. image:: /_static/examples/progressbar-variants-light.png
   :class: bs-screenshot-light
   :alt: ProgressBar thin and vertical variants — light theme

.. image:: /_static/examples/progressbar-variants-dark.png
   :class: bs-screenshot-dark
   :alt: ProgressBar thin and vertical variants — dark theme

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

The complete reference for :class:`ProgressBar <bootstack.ProgressBar>` lives on
the :doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ProgressBar

Full Example
------------

.. literalinclude:: ../../docs/examples/progressbar.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs