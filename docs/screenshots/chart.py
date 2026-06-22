"""Screenshot scenes for the Chart widget.

Requires the visualization extra (``pip install bootstack[viz-seaborn]``). Each
scene builds a small, self-contained figure so no external data is needed.
"""

import math

import bootstack as bs


def _series(fn, n=80, scale=1.0):
    xs = [i / 10 for i in range(n)]
    return xs, [fn(x) * scale for x in xs]


def hero():
    """A themed multi-series line chart via the managed render path."""
    def render(ax):
        for label, fn in (("signal", math.sin), ("filtered", math.cos),
                          ("model", lambda x: math.sin(x) * 0.5)):
            xs, ys = _series(fn)
            ax.plot(xs, ys, label=label, linewidth=2)
        ax.set_title("Signal analysis")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("amplitude")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    with bs.App(title="Chart", size=(620, 420), padding=16) as app:
        bs.Chart(render=render, grow=True, horizontal="stretch")
    app.run()


def toolbar():
    """A chart with the themed navigation toolbar (pan / zoom / save)."""
    def render(ax):
        xs, ys = _series(math.sin)
        ax.plot(xs, ys, linewidth=2)
        ax.fill_between(xs, ys, alpha=0.15)
        ax.set_title("Pan and zoom with the toolbar")
        ax.grid(True, alpha=0.3)

    with bs.App(title="Chart — Toolbar", size=(620, 440), padding=16) as app:
        chart = bs.Chart(render=render, toolbar=True, grow=True, horizontal="stretch")
        # Author buttons sit beside the built-in navigation tools.
        chart.toolbar.add_divider()
        chart.toolbar.add_button(icon="arrow-clockwise", on_click=chart.draw)
        chart.toolbar.add_widget(bs.ThemeToggle)
    app.run()


def seaborn():
    """A seaborn bar chart seeded with the theme's accent palette."""
    import seaborn as sns

    def render(ax):
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        regions = ["North", "South", "East"]
        data = {"quarter": [], "region": [], "revenue": []}
        for i, q in enumerate(quarters):
            for j, r in enumerate(regions):
                data["quarter"].append(q)
                data["region"].append(r)
                data["revenue"].append(20 + 8 * i + 5 * j)
        sns.barplot(data=data, x="quarter", y="revenue", hue="region", ax=ax)
        ax.set_title("Revenue by quarter")
        ax.set_xlabel("")

    with bs.App(title="Chart — Seaborn", size=(620, 420), padding=16) as app:
        bs.Chart(render=render, grow=True, horizontal="stretch")
    app.run()


SCENES = {
    "hero": hero,
    "toolbar": toolbar,
    "seaborn": seaborn,
}
