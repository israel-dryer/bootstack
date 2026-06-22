Live and data-driven charts
===========================

Bind a chart to reactive state so it redraws itself — from a `Signal`, or from a
data source it shares with a table.

.. image:: /_static/examples/visualizing_data-live-light.png
   :class: bs-screenshot-light
   :alt: A chart and a table on one data source — light theme

.. image:: /_static/examples/visualizing_data-live-dark.png
   :class: bs-screenshot-dark
   :alt: A chart and a table on one data source — dark theme

How it works
------------

The managed ``render`` path becomes reactive the moment you bind a source. Two
ways to do it.

From a signal
~~~~~~~~~~~~~

Pass a :class:`~bootstack.Signal` and ``render`` receives its value; the chart
re-renders whenever the signal changes — so any control bound to that signal
drives the chart:

.. code-block:: python

   count = bs.Signal(20)

   def render(ax, n):
       ax.plot(range(n), [i * i for i in range(n)])

   bs.Chart(render=render, signal=count, grow=True)
   bs.Slider(signal=count, min_value=5, max_value=80)   # drag → chart redraws

From a data source
~~~~~~~~~~~~~~~~~~

Pass a ``data_source`` and ``render`` receives the source's records (a list of
dicts). The chart re-renders whenever the source changes — so a chart and a
:doc:`DataTable </widgets/datatable>` on the **same** source stay in lockstep:

.. code-block:: python

   from bootstack.data import MemoryDataSource

   ds = MemoryDataSource()
   ds.load([{"month": "Jan", "sales": 120}, {"month": "Feb", "sales": 180}])

   def render(ax, rows):
       ax.bar([r["month"] for r in rows], [r["sales"] for r in rows])

   bs.Chart(render=render, data_source=ds, grow=True)
   bs.DataTable(data_source=ds, columns=["month", "sales"])

Insert a record into the source and both views update. The chart reads the
source's current *filtered and sorted* view, so calling ``ds.where(...)`` or
``ds.order(...)`` reshapes the plot too:

.. code-block:: python

   from bootstack.data import col

   ds.where(col("sales") >= 150)   # both the chart and the table follow

.. note::

   matplotlib's ``draw()`` is not free. For a high-frequency source or signal,
   pass ``debounce=<ms>`` to coalesce a burst of changes into one redraw; the
   chart also skips redraws while it is off-screen.

Example
-------

A chart and a table on one source, with a filter toggle and an "add" button —
every change flows to both views:

.. literalinclude:: ../../examples/visualizing_data/live_charts.py
   :language: python
   :linenos:
   :start-after: from bootstack.data import MemoryDataSource, col

When to use
-----------

Use ``signal=`` when the chart reflects a single reactive value (a control, a
computed result); use ``data_source=`` when it visualizes records you also show
elsewhere. For the data-source model in depth, see
:doc:`/tasks/displaying-data` and :doc:`/reference/data-sources`. For continuous,
high-rate motion, :doc:`animated-charts` is the better tool than a fast signal.
