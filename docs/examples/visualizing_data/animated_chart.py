"""Real-time and animated charts — a smooth, blitting animation.

Run this directly (and record it!). Requires the visualization extra:
``pip install bootstack[viz]``.

``chart.animate(setup, update)`` is the fast path for continuous motion: it
updates artists in place and redraws only them over a cached background (blitting)
instead of rebuilding the figure each frame. ``setup`` runs once to create the
artists and set FIXED axis limits (blitting needs stable axes) — it returns the
artist, or a list of artists, to animate. ``update`` runs every frame with the
elapsed time in seconds, so the motion's speed stays constant even when frame
timing jitters.

The animation pauses automatically when the chart is hidden (a switched-away tab,
a minimized window) and resumes when shown, and stops when the widget is
destroyed.
"""
import math

import bootstack as bs

XS = [i / 12 for i in range(180)]   # dense sampling → smooth curves
MID = XS[len(XS) // 2]


def signal(x, t):
    return math.sin(x - t * 2.2)


def filtered(x, t):
    return 0.7 * math.cos(x * 1.3 - t * 1.6)


def setup(ax):
    """Create every artist once, pin the axes, and return them to animate."""
    (sig_line,) = ax.plot([], [], linewidth=2.5, label="signal")
    (flt_line,) = ax.plot([], [], linewidth=2.5, label="filtered")
    (dot,) = ax.plot([], [], "o", markersize=10, markerfacecolor="white",
                     markeredgecolor=sig_line.get_color(), markeredgewidth=2.5)
    ax.set_xlim(0, XS[-1])
    ax.set_ylim(-1.3, 1.3)
    ax.set_xlabel("time")
    ax.set_ylabel("amplitude")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")
    return [sig_line, flt_line, dot]


def update(t, artists):
    """Each frame: travel the waves and let the dot ride the signal."""
    sig_line, flt_line, dot = artists
    sig_line.set_data(XS, [signal(x, t) for x in XS])
    flt_line.set_data(XS, [filtered(x, t) for x in XS])
    dot.set_data([MID], [signal(MID, t)])


with bs.App(title="Animated chart", size=(680, 440), padding=16, gap=12) as app:
    bs.Label("A blitting animation — smooth at high frame rates", font="heading-md")
    chart = bs.Chart(grow=True, horizontal="stretch")
    anim = chart.animate(setup, update, interval=20)

    with bs.Row(gap=8):
        bs.Button("Pause", on_click=anim.stop)
        bs.Button("Resume", accent="primary", on_click=anim.start)

app.run()
