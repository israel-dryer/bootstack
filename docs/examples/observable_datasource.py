"""Observable data source — a live dashboard fed from a background thread.

A worker thread mutates a shared ``MemoryDataSource`` every 600 ms. Nothing
calls ``reload()``: the bound ``ListView`` refreshes itself, a ``Badge`` tracks
the row count through ``on_change``, and a ``Gauge`` tracks the active-row count
through ``observe`` — all updated on the UI thread automatically.

Run with:
    python docs/examples/observable_datasource.py
"""

import random
import threading

import bootstack as bs
from bootstack.data import MemoryDataSource
from bootstack.data import col

NAMES = ["Alice", "Bob", "Carol", "David", "Eva", "Frank", "Grace", "Henry"]
STATUSES = ["active", "idle", "offline"]
ICONS = {"active": "check-circle-fill", "idle": "clock", "offline": "x-circle"}


def row(name: str, status: str) -> dict:
    """Build a record. `title`/`text`/`icon` drive the ListView display; the
    `status` field backs the observed query."""
    return {
        "title": name,
        "text": f"Status: {status}",
        "icon": ICONS[status],
        "status": status,
    }


# A shared source — the feed writes to it, the widgets read from it.
ds = MemoryDataSource().load([row(n, "active") for n in NAMES[:3]])

_stop = threading.Event()


def feed() -> None:
    """Background worker — inserts, updates, and removes rows off the UI thread."""
    while not _stop.wait(0.6):
        roll = random.random()
        if roll < 0.5 or ds.count < 3:
            ds.insert(row(random.choice(NAMES), random.choice(STATUSES)))
        elif roll < 0.8:
            rows = ds.page_slice(0, ds.count)
            target = random.choice(rows)
            status = random.choice(STATUSES)
            ds.update(target["id"], {"text": f"Status: {status}",
                                     "icon": ICONS[status], "status": status})
        else:
            rows = ds.page_slice(0, ds.count)
            ds.delete(random.choice(rows)["id"])


with bs.App(title="Observable data source", size=(560, 560), padding=16, gap=12) as app:
    bs.Label("Live feed dashboard", font="heading-md")

    with bs.Row(gap=16, vertical_items="center"):
        total = bs.Badge("0 rows", accent="primary")
        active_gauge = bs.Gauge(value=0, max_value=20, accent="success")

    bs.Label("Bound ListView (auto-refreshing):", font="caption")
    bs.ListView(data_source=ds, grow=True, horizontal="stretch")

    # Badge tracks total row count via the coarse change stream.
    total_sub = ds.on_change().map(lambda e: ds.count).listen(
        lambda n: setattr(total, "text", f"{n} rows")
    )

    # Gauge tracks the active-row count via an observed query.
    active_sub = ds.observe(col("status") == "active").listen(
        lambda rows: setattr(active_gauge, "value", len(rows))
    )

worker = threading.Thread(target=feed, daemon=True)
worker.start()
app.run()          # blocks until the window closes
_stop.set()        # stop the feed once the UI is gone
