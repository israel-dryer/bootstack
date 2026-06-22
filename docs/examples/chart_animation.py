"""Chart animation — a smooth, high-FPS plot via blitting.

Run this directly. Requires the visualization extra: ``pip install bootstack[viz]``.
The wave scrolls smoothly because ``chart.animate`` updates the line's data in
place and blits only that line over a cached background (instead of rebuilding
the whole figure each frame), and because the motion is driven by *elapsed time*
rather than the frame count — so it keeps a constant speed even if frame timing
jitters. Pause/Play control it; toggle the theme and it keeps running, recolored.

Use this for continuous animation. For event-driven updates that change the
plotted data occasionally (e.g. a control), use the ``render=`` path instead —
see chart_reactive.py.
"""

import numpy as np

import bootstack as bs

xs = np.linspace(0, 12, 240)  # fixed x grid


def setup(ax):
    """Create the artists once and fix the axes (blitting needs stable axes)."""
    (line,) = ax.plot(xs, np.zeros_like(xs), linewidth=2)
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(-1.2, 1.2)
    ax.set_title("Live animation (blitting)")
    return line


def frame(t, line):
    """Per frame: `t` is elapsed seconds — motion at a constant 2 rad/s."""
    line.set_ydata(np.sin(xs + t * 2.0))


with bs.App(title="Chart animation", min_size=(680, 480), padding=16, gap=12) as app:
    chart = bs.Chart(grow=True, horizontal="stretch")
    anim = chart.animate(setup, frame, interval=16)  # ~60 fps target

    with bs.Row(gap=8):
        bs.Button("Pause", on_click=anim.stop)
        bs.Button("Play", on_click=anim.start)
        bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()