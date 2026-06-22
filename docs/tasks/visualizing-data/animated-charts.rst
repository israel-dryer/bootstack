Real-time and animated charts
=============================

Drive smooth, continuous motion — a live waveform, a streaming metric — without
rebuilding the figure each frame.

.. raw:: html

   <video class="bs-video-light" autoplay loop muted playsinline controls
          aria-label="An animated chart — flowing waves drawn by blitting">
     <source src="../../_static/examples/chart-animation-video-light.mp4" type="video/mp4">
   </video>
   <video class="bs-video-dark" autoplay loop muted playsinline controls
          aria-label="An animated chart — flowing waves drawn by blitting">
     <source src="../../_static/examples/chart-animation-video-dark.mp4" type="video/mp4">
   </video>

How it works
------------

The managed ``render`` path rebuilds the whole figure on each update — right for
occasional data changes, but limited to roughly 30 fps. For continuous motion,
``chart.animate(setup, update)`` is the fast path: it updates artists *in place*
and redraws only them over a cached background (blitting), sustaining high frame
rates.

.. code-block:: python

   import math

   xs = [i / 20 for i in range(140)]

   def setup(ax):
       (line,) = ax.plot([], [])
       ax.set_xlim(0, xs[-1])          # FIXED limits — blitting needs stable axes
       ax.set_ylim(-1.2, 1.2)
       return line                     # the artist(s) to animate

   def update(t, line):                # t = elapsed seconds
       line.set_data(xs, [math.sin(x - t * 2) for x in xs])

   chart = bs.Chart(grow=True)
   anim = chart.animate(setup, update, interval=30)

``setup`` runs **once** to create the artists and set fixed axis limits (blitting
needs stable axes). ``update`` runs every frame with the elapsed time in
**seconds** — drive motion by ``t`` and the apparent speed stays constant even
when frame timing jitters. Mutate the artist's data in place; don't create new
artists or rescale the axes.

``animate`` returns a handle: ``anim.stop()`` / ``anim.start()`` pause and resume,
and ``anim.running`` reports the state. The animation also **pauses itself when
the chart is hidden** (a switched-away tab, a minimized window) and resumes when
shown, so off-screen charts on a dashboard cost nothing; it stops when the widget
is destroyed.

.. note::

   For a live data feed, keep a rolling window of recent samples and set the
   artist's data from it in ``update`` — the same blitting path, fed by your
   incoming data instead of a clock.

Example
-------

.. literalinclude:: ../../examples/visualizing_data/animated_chart.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs

When to use
-----------

Use ``animate`` for continuous, high-rate motion (waveforms, live sensors,
progress). For occasional updates — a value changes, a record is added — the
reactive ``render`` path in :doc:`live-charts` is simpler and enough. The full
animation reference is on the :doc:`Chart guide </widgets/chart>`.
