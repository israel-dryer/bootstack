Statistical plots with seaborn
==============================

Draw seaborn's statistical plots — bars, boxes, distributions — onto a themed,
on-brand chart.

.. image:: /_static/examples/visualizing_data-statistical-light.png
   :class: bs-screenshot-light
   :alt: A seaborn grouped bar chart — light theme

.. image:: /_static/examples/visualizing_data-statistical-dark.png
   :class: bs-screenshot-dark
   :alt: A seaborn grouped bar chart — dark theme

How it works
------------

`seaborn <https://seaborn.pydata.org/>`_ draws onto a matplotlib `Axes`, and a
managed ``render`` callback hands you exactly that — so seaborn works with no
special integration. Call it with ``ax=ax``:

.. code-block:: python

   import seaborn as sns

   def render(ax):
       sns.barplot(data=rows, x="quarter", y="revenue", hue="region", ax=ax)

   bs.Chart(render=render, grow=True)

When seaborn is installed and imported, ``Chart`` seeds its palette from the
theme's accent colors, so a categorical plot is on-brand and flips with
light/dark — no ``palette=`` needed. Because seaborn's plots are usually
area-filled (bars, violins, KDE), the seeded colors are softened from the full
accent saturation; tune that with ``seaborn_desat`` (``0``–``1``, default
``0.75``), or pass an explicit ``palette=`` to override entirely.

.. note::

   Install the extra with ``pip install bootstack[viz-seaborn]``. seaborn stays
   off the import path — ``Chart`` only seeds its palette when *you* have imported
   seaborn.

The same axes takes any seaborn plot — swap the one call for the chart you need:

.. code-block:: python

   sns.boxplot(data=rows, x="group", y="value", ax=ax)        # distributions
   sns.violinplot(data=rows, x="group", y="value", ax=ax)
   sns.heatmap(matrix, ax=ax)                                 # a matrix
   sns.regplot(data=rows, x="x", y="y", ax=ax)                # a fit line

Example
-------

.. literalinclude:: ../../examples/visualizing_data/statistical_plots.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs

When to use
-----------

Reach for seaborn when you want statistical summaries — grouped bars, box and
violin plots, heatmaps, regressions — with minimal code. For plain line/bar/
scatter plots, matplotlib alone is enough (:doc:`plotting-data`). seaborn plots
are reactive too: drive them from a signal or data source exactly as in
:doc:`live-charts`. Palette and ``seaborn_desat`` details are on the
:doc:`Chart guide </widgets/chart>`.
