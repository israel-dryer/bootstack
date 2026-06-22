Chart
=====

Embeds a matplotlib figure as a themed widget that recolors with the app.

.. image:: /_static/examples/chart-hero-light.png
   :class: bs-screenshot-light
   :alt: Chart — light theme

.. image:: /_static/examples/chart-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Chart — dark theme

Usage
-----

``Chart`` is the bridge between bootstack and the scientific Python plotting
stack. You draw with matplotlib (or seaborn, which draws onto the same axes) and
the chart owns the rest: it embeds the figure as a first-class widget that fills
its space, recolors its chrome — figure and axes backgrounds, spines, ticks, and
text — to match the active theme, and flips with light/dark like everything else.

``Chart`` is deliberately *not* a plotting API. It does not wrap matplotlib's
drawing calls, so you keep the full expressive power of matplotlib and seaborn;
bootstack owns only embedding, theming, and the redraw loop.

.. note::

   matplotlib is an optional dependency. Install it with the visualization
   extra: ``pip install bootstack[viz]`` (or ``bootstack[viz-seaborn]`` to add
   seaborn). Constructing a ``Chart`` without matplotlib installed raises a
   :class:`BootstackError <bootstack.errors.BootstackError>` explaining how to
   install it.

The mental model: two modes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two ways to use a chart, and which one you pick decides how much
bootstack does for you:

- **Figure host** — you build a :class:`~matplotlib.figure.Figure` and hand it
  over. The chart embeds it and recolors its chrome to the theme. You own the
  figure; theming the *data series* is up to you.
- **Managed render** — you pass a ``render`` callback and a reactive source. The
  chart owns the figure and the redraw loop: each redraw clears the axes, applies
  the theme (including a semantic accent color cycle), then calls your ``render``.
  It re-renders when the theme changes or when the bound data changes.

Reach for the managed path whenever the plot reflects live state — it is what
makes a chart reactive *and* fully themed. Use the figure host for a one-off
figure you have already built.

Build figures with matplotlib's object API (:class:`~matplotlib.figure.Figure`),
never ``pyplot`` — an embedded figure must be a standalone object, and ``pyplot``
would also pop a separate OS window.

Hosting a figure
~~~~~~~~~~~~~~~~

Build a figure and pass it as the first argument. The chart embeds it and themes
its chrome:

.. code-block:: python

   from matplotlib.figure import Figure

   fig = Figure()
   ax = fig.add_subplot(111)
   ax.plot([1, 2, 3], [4, 5, 6])
   bs.Chart(fig, grow=True)

``chart.figure`` is a live property — assign a new figure to swap what is shown.
For quick, imperative plotting, ``chart.ax`` returns the figure's primary axes
(creating one if the figure is empty); call ``chart.draw()`` after mutating it::

   chart = bs.Chart()
   chart.ax.plot([1, 2, 3])
   chart.draw()

Managed render and live data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pass a ``render`` callback to let the chart own the redraw. Bind it to a
:class:`~bootstack.Signal` and the chart re-renders whenever the signal changes —
just draw, the chart clears and re-themes the axes for you:

.. code-block:: python

   count = bs.Signal(20)

   def render(ax, n):
       ax.plot(range(n), [i * i for i in range(n)])

   bs.Chart(render=render, signal=count, grow=True)   # redraws when count changes

Bind a ``data_source`` instead and ``render`` receives the source's records (a
list of dicts). The chart re-renders whenever the source changes — so a chart and
a :doc:`DataTable <datatable>` can share one source and stay in lockstep:

.. code-block:: python

   from bootstack.data import MemoryDataSource

   ds = MemoryDataSource()
   ds.load([{"month": "Jan", "sales": 12}, {"month": "Feb", "sales": 18}])

   def render(ax, rows):
       ax.bar([r["month"] for r in rows], [r["sales"] for r in rows])

   bs.Chart(render=render, data_source=ds, grow=True)

The chart reads the source's current filtered/sorted view, so calling ``where()``
or ``order()`` on the source reshapes the plot. For a high-frequency source, pass
``debounce=<ms>`` to coalesce rapid changes into one render.

Theming and the accent cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the managed path the chart runs your ``render`` under the theme's matplotlib
settings, including a semantic color cycle drawn from the accent roles
(``primary``, ``success``, ``info``, ``warning``, ``danger``, ``secondary``). So
multiple series are on-brand without you naming a single color — the first plot is
``primary``, the second ``success``, and so on, and they recolor on a theme
change.

This automatic styling governs the managed path only. A figure you build and pass
as a host already owns its series colors, so the chart only recolors its *chrome*
(faces, spines, ticks, text) — a fully bespoke figure styles itself.

To keep your own series colors while still letting the chart fit the app, pass
``themed=False``. The chrome (background, axes, text, ticks, grid) still tracks
the theme — so the chart never floats as a mismatched panel — but the accent
cycle and seaborn palette are not imposed, leaving the data colors to you (or to
your own matplotlib style). Colors you set explicitly on a series always win
regardless::

   bs.Chart(render=render, signal=count, themed=False, grow=True)

Navigation toolbar
~~~~~~~~~~~~~~~~~~

Pass ``toolbar=True`` to add a themed navigation toolbar above the chart, with
home / back / forward history, pan, zoom-to-rectangle, and save:

.. code-block:: python

   bs.Chart(render=render, signal=count, toolbar=True, grow=True)

.. image:: /_static/examples/chart-toolbar-light.png
   :class: bs-screenshot-light
   :alt: Chart navigation toolbar — light theme

.. image:: /_static/examples/chart-toolbar-dark.png
   :class: bs-screenshot-dark
   :alt: Chart navigation toolbar — dark theme

Pan and zoom drive matplotlib's own navigation, so they work on any embedded
figure; the active tool is highlighted in the bar, and the coordinate readout
follows the cursor. Save opens bootstack's file dialog and writes a PNG, PDF, or
SVG.

To include only some of the standard tools, pass a list instead of ``True`` —
the named tools appear in that order, with dividers grouping them:

.. code-block:: python

   bs.Chart(render=render, toolbar=["pan", "zoom", "save"], grow=True)

The tool names are ``home``, ``back``, ``forward``, ``pan``, ``zoom``, and
``save``. Pass ``[]`` for an empty bar you fill entirely yourself.

The toolbar is also yours to extend. ``chart.toolbar`` returns a
:doc:`Toolbar <toolbar>` — add your own buttons (a refresh, an export, a theme
toggle) and they sit beside the built-in tools:

.. code-block:: python

   chart = bs.Chart(render=render, signal=count, toolbar=True, grow=True)
   chart.toolbar.add_divider()
   chart.toolbar.add_button(icon="arrow-clockwise", on_click=refresh)
   chart.toolbar.add_widget(bs.ThemeToggle)

Seaborn
~~~~~~~

`seaborn <https://seaborn.pydata.org/>`_ draws onto a matplotlib axes, so it works
inside a ``render`` callback with no special integration — call it with
``ax=ax``. When seaborn is installed (the ``viz-seaborn`` extra) and imported, the
chart seeds its palette from the same accent cycle, so a categorical plot picks up
the theme's colors:

.. code-block:: python

   import seaborn as sns

   def render(ax, rows):
       sns.barplot(data=rows, x="quarter", y="revenue", hue="region", ax=ax)

   bs.Chart(render=render, data_source=ds, grow=True)

.. image:: /_static/examples/chart-seaborn-light.png
   :class: bs-screenshot-light
   :alt: Seaborn chart themed with accent colors — light theme

.. image:: /_static/examples/chart-seaborn-dark.png
   :class: bs-screenshot-dark
   :alt: Seaborn chart themed with accent colors — dark theme

Because seaborn plots are usually area-filled (bars, violins, KDE), the seeded
palette is softened from the full accent saturation to suit that look. Tune it
with ``seaborn_desat`` (``0``–``1``; default ``0.75``) — pass ``1.0`` to keep the
accents fully saturated, or give your seaborn call an explicit ``palette=`` to
override entirely.

Animation
~~~~~~~~~

For continuous motion, ``animate`` is the fast path. The managed ``render`` path
rebuilds the whole figure on each update — right for occasional data changes, but
limited to roughly 30 fps. Animation instead updates artists in place and redraws
only them over a cached background, sustaining high frame rates:

.. code-block:: python

   import math

   def setup(ax):
       (line,) = ax.plot([], [])
       ax.set_xlim(0, 2 * math.pi)        # fixed limits — blitting needs stable axes
       ax.set_ylim(-1, 1)
       return line

   def update(t, line):                    # t is elapsed seconds
       xs = [i / 20 for i in range(126)]
       line.set_data(xs, [math.sin(x - t) for x in xs])

   chart = bs.Chart()
   anim = chart.animate(setup, update, interval=30)
   # anim.stop() / anim.start() to control it

``setup`` runs once to create the artists and set fixed axis limits; ``update``
runs each frame with the elapsed time in seconds, so apparent speed stays constant
under timer jitter. The animation pauses automatically when the chart is hidden (a
switched-away tab, a minimized window) and resumes when shown, and stops when the
widget is destroyed.

.. raw:: html

   <video class="bs-video-light" autoplay loop muted playsinline controls
          aria-label="An animated chart — flowing waves drawn by blitting">
     <source src="../_static/examples/chart-animation-video-light.mp4" type="video/mp4">
   </video>
   <video class="bs-video-dark" autoplay loop muted playsinline controls
          aria-label="An animated chart — flowing waves drawn by blitting">
     <source src="../_static/examples/chart-animation-video-dark.mp4" type="video/mp4">
   </video>

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

A chart fills the space it is given. Pass ``grow=True`` (and
``horizontal="stretch"`` in a column) so it expands to fill its container.

See also
--------

- :doc:`/tasks/displaying-data` — backing widgets with a data source.
- :class:`Signal <bootstack.Signal>` — the reactive value a managed chart binds
  to.
- :doc:`datatable` — pair a table and a chart on one data source.

API
---

The complete reference for :class:`Chart <bootstack.Chart>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Chart

Full Example
------------

.. literalinclude:: ../../docs/examples/chart.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
