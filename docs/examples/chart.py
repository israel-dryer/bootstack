"""Chart — embed a matplotlib figure as a themed bootstack widget.

Run this directly to see the widget. Requires the visualization extra:
``pip install bootstack[viz]``. Click "Toggle theme" to watch the chart's
background and text recolor with the rest of the app.

Build figures with matplotlib's object API (``matplotlib.figure.Figure``), not
``pyplot`` — an embedded figure must be a standalone object.
"""

import math

from matplotlib.figure import Figure

import bootstack as bs


def build_figure() -> Figure:
    """A small two-series line plot."""
    fig = Figure(figsize=(5.5, 3.6))
    ax = fig.add_subplot(111)
    xs = [i / 12 for i in range(80)]
    ax.plot(xs, [math.sin(x) for x in xs], label="sin")
    ax.plot(xs, [math.cos(x) for x in xs], label="cos")
    ax.set_title("Trigonometric curves")
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.legend(loc="upper right")
    return fig


with bs.App(title="Chart", size=(640, 480), padding=16, gap=12) as app:
    bs.Label("A matplotlib figure, themed to match the app", font="heading-md")
    bs.Chart(build_figure(), grow=True, horizontal="stretch")
    bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()