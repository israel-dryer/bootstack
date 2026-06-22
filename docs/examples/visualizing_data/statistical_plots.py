"""Statistical plots with seaborn — drawn onto the Chart's themed axes.

Run this directly. Requires the seaborn extra:
``pip install bootstack[viz-seaborn]``.

seaborn draws onto a matplotlib `Axes`, so it works inside a ``render`` callback
with no special integration — call it with ``ax=ax``. When seaborn is installed
and imported, the chart seeds its palette from the theme's accent colors (softened
to suit seaborn's fill-heavy look), so a categorical plot is on-brand and flips
with light/dark.
"""
import seaborn as sns

import bootstack as bs

# A small tidy dataset: revenue by quarter, split by region.
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
REGIONS = ["North", "South", "East"]
DATA = {"quarter": [], "region": [], "revenue": []}
for i, q in enumerate(QUARTERS):
    for j, r in enumerate(REGIONS):
        DATA["quarter"].append(q)
        DATA["region"].append(r)
        DATA["revenue"].append(20 + 8 * i + 5 * j)


def render(ax):
    """A grouped bar chart — seaborn picks up the seeded accent palette."""
    sns.barplot(data=DATA, x="quarter", y="revenue", hue="region", ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("revenue ($k)")


with bs.App(title="Statistical plots", size=(640, 460), padding=16, gap=12) as app:
    bs.Label("A seaborn bar chart, on-brand and themed", font="heading-md")
    bs.Chart(render=render, grow=True, horizontal="stretch")
    bs.Button("Toggle theme", on_click=bs.toggle_theme)

app.run()
