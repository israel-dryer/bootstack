"""Plotting your data — a managed Chart that themes itself.

Run this directly. Requires the visualization extra:
``pip install bootstack[viz]``.

In the managed ``render=`` path you never touch the figure: you draw on the
`Axes` and the chart owns clearing, theming, and the redraw. Multiple series pick
up the theme's accent colors automatically, and everything flips with light/dark.
"""
import math

import bootstack as bs


def render(ax):
    """Draw two themed series — colors come from the accent cycle."""
    xs = [i / 10 for i in range(80)]
    ax.plot(xs, [math.sin(x) for x in xs], label="sin", linewidth=2)
    ax.plot(xs, [math.cos(x) for x in xs], label="cos", linewidth=2)
    ax.set_xlabel("x")
    ax.set_ylabel("amplitude")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")


with bs.App(title="Plotting your data", size=(640, 460), padding=16, gap=12) as app:
    bs.Label("Two series, themed to match the app", font="heading-md")
    bs.Chart(render=render, grow=True, horizontal="stretch")
    bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()
