Plotting your data
==================

Draw a chart from your data and let it theme itself — the starting point for
everything else in this set.

.. image:: /_static/examples/visualizing_data-plotting-light.png
   :class: bs-screenshot-light
   :alt: A two-series line chart — light theme

.. image:: /_static/examples/visualizing_data-plotting-dark.png
   :class: bs-screenshot-dark
   :alt: A two-series line chart — dark theme

How it works
------------

:class:`~bootstack.Chart` embeds a matplotlib figure as a first-class widget. The
recommended way to use it is the **managed render** path: you pass a ``render``
callback and the chart owns the rest — each redraw clears the axes, applies the
theme, calls your ``render(ax)``, and draws. You just plot:

.. code-block:: python

   import math

   def render(ax):
       xs = [i / 10 for i in range(80)]
       ax.plot(xs, [math.sin(x) for x in xs], label="sin")
       ax.plot(xs, [math.cos(x) for x in xs], label="cos")
       ax.legend()

   bs.Chart(render=render, grow=True, horizontal="stretch")

You draw with plain matplotlib — ``Chart`` is not a plotting API, so you keep its
full expressive power. It owns embedding, theming, and the redraw.

Multiple series are themed automatically: the first line is ``primary``, the
second ``success``, and so on, drawn from the theme's accent colors. The chrome —
figure and axes backgrounds, spines, ticks, text — matches the active surface and
flips with light/dark, so a ``bs.toggle_theme()`` recolors the whole chart with
the rest of the app.

.. note::

   matplotlib is an optional dependency. Install it with
   ``pip install bootstack[viz]``. Build figures with matplotlib's object API
   (:class:`~matplotlib.figure.Figure`), never ``pyplot`` — an embedded figure
   must be a standalone object.

Drawing your own figure
~~~~~~~~~~~~~~~~~~~~~~~~

If you already have a :class:`~matplotlib.figure.Figure` — or want full control
over the styling — hand it over directly. The chart embeds it and recolors only
its chrome to the theme; the data series are yours:

.. code-block:: python

   from matplotlib.figure import Figure

   fig = Figure()
   fig.add_subplot(111).plot([1, 2, 3], [4, 5, 6])
   bs.Chart(fig, grow=True)

Reach for the managed ``render`` path whenever the plot reflects live state — it
is what makes the next two guides (signals and data sources) reactive.

Example
-------

.. literalinclude:: ../../examples/visualizing_data/plotting_data.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs

When to use
-----------

This is the foundation. When the plot should update as your state changes, bind a
:class:`~bootstack.Signal` or a data source — see :doc:`live-charts`. For
statistical plots (bars, boxes, distributions) reach for seaborn —
:doc:`statistical-plots`. For continuous motion, :doc:`animated-charts`. The full
widget reference is the :doc:`Chart guide </widgets/chart>`.
