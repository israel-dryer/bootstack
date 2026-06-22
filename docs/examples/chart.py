"""Chart — embed a matplotlib figure as a themed, reactive bootstack widget.

Run this directly to see the widget. Requires the visualization extra:
``pip install bootstack[viz]``. Drag the slider to redraw the chart from a
`Signal`, use the toolbar to pan / zoom / save, and click "Toggle theme" to
watch the chart recolor with the rest of the app.

Build figures with matplotlib's object API (``matplotlib.figure.Figure``), not
``pyplot`` — an embedded figure must be a standalone object. In the managed
``render=`` path below you never touch the figure directly: just draw on the
axes and the chart owns clearing, theming, and the redraw.
"""

import math

import bootstack as bs

with bs.App(title="Chart", size=(680, 520), padding=16, gap=12) as app:
    points = bs.Signal(60)

    def render(ax, n):
        """Draw two themed series; colors come from the accent cycle."""
        xs = [i / 8 for i in range(n)]
        ax.plot(xs, [math.sin(x) for x in xs], label="sin", linewidth=2)
        ax.plot(xs, [math.cos(x) for x in xs], label="cos", linewidth=2)
        ax.set_title("Trigonometric curves")
        ax.set_xlabel("x")
        ax.set_ylabel("amplitude")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    bs.Label("A reactive matplotlib figure, themed to match the app",
             font="heading-md")
    bs.Chart(render=render, signal=points, toolbar=True,
             grow=True, horizontal="stretch")

    with bs.Row(gap=12, horizontal="stretch"):
        bs.Label("Points")
        bs.Slider(signal=points, min_value=10, max_value=120, grow=True)
        bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()
