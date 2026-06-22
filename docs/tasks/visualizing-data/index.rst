Visualizing Data
================

:class:`Chart <bootstack.Chart>` embeds a matplotlib (and seaborn) figure as a
first-class widget — one that themes itself, flips with light/dark, and
live-updates from a `Signal` or a data source. You draw with plain
matplotlib/seaborn; bootstack owns embedding, theming, and the redraw.

This set goes from a first plot to live dashboards, statistical charts, and
real-time animation. Start at the top and work down, or jump to what you need.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Plotting your data
      :link: plotting-data
      :link-type: doc

      The foundation — a managed ``render`` callback that themes itself, the
      accent color cycle, and the figure-host escape hatch.

   .. grid-item-card:: Live and data-driven charts
      :link: live-charts
      :link-type: doc

      Bind a chart to a ``Signal`` or a ``DataSource`` so it redraws itself — and
      keep a chart and a table in lockstep on one source.

   .. grid-item-card:: Statistical plots with seaborn
      :link: statistical-plots
      :link-type: doc

      Draw seaborn's bars, boxes, and distributions onto a themed, on-brand chart
      — palette seeded from the theme accents.

   .. grid-item-card:: Real-time and animated charts
      :link: animated-charts
      :link-type: doc

      Drive smooth, continuous motion with blitting — a live waveform or a
      streaming metric, at high frame rates.

.. seealso::

   For the full ``Chart`` API — every option, ``toolbar=``, ``animate``, the
   theme bridge — see the :doc:`Chart widget guide </widgets/chart>`. Install the
   engine with the ``viz`` (or ``viz-seaborn``) extra.

.. toctree::
   :hidden:

   plotting-data
   live-charts
   statistical-plots
   animated-charts
