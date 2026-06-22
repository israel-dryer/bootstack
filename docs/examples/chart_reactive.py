"""Chart (reactive) — a managed render that redraws when bound data changes.

Run this directly. Requires the visualization extra: ``pip install bootstack[viz]``.
The ``render=`` path rebuilds the figure whenever a bound `Signal` changes —
ideal for event-driven updates like a control changing a parameter. Drag the
slider to change the wave's frequency; the chart re-renders with the theme's
accent color cycle. Click "Toggle theme" to recolor.

For smooth, high-FPS animation (a continuously moving plot), use
``chart.animate(...)`` instead — see chart_animation.py.
"""

import math

import bootstack as bs


def render(ax, frequency: float) -> None:
    """Plot sine and cosine at the bound frequency. `ax` arrives themed."""
    xs = [i * 0.1 for i in range(120)]
    ax.plot(xs, [math.sin(frequency * x) for x in xs], label="sin")
    ax.plot(xs, [math.cos(frequency * x) for x in xs], label="cos")
    ax.set_ylim(-1.2, 1.2)
    ax.set_title(f"frequency = {frequency:.1f}")
    ax.legend(loc="upper right")


with bs.App(title="Reactive Chart", min_size=(640, 480), padding=16, gap=12) as app:
    # A Signal must be created inside the running app (the event loop must exist).
    freq = bs.Signal(1.0)

    bs.Label("Drag the slider — the chart re-renders", font="heading-md")
    bs.Chart(render=render, signal=freq, grow=True, horizontal="stretch")

    with bs.Row(gap=8, horizontal="stretch"):
        bs.Label("Frequency")
        bs.Slider(min_value=0.2, max_value=4.0, signal=freq, grow=True)
    bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()