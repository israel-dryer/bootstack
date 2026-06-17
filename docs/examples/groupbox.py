"""GroupBox — full feature demo.

Demonstrates title label, accent borders, layout modes, and in-context usage.

Run with:
    python docs/examples/groupbox.py
"""

import bootstack as bs

with bs.App(title="GroupBox Demo", padding=20, gap=16) as app:

    # Accent borders
    bs.Label("Accent Borders", font="heading-sm")
    with bs.Row(gap=12):
        for accent in ("default", "primary", "secondary", "success", "warning", "danger"):
            with bs.GroupBox(accent.title(), accent=accent, padding=10, gap=4):
                bs.Label("Item one")
                bs.Label("Item two")

    # Layout modes
    bs.Label("Layout Modes", font="heading-sm")
    with bs.Row(gap=12):

        with bs.GroupBox("Column (default)", padding=10, gap=8):
            bs.Label("First")
            bs.Label("Second")
            bs.Label("Third")

        with bs.GroupBox("Row", layout="row", padding=10, gap=12, vertical_items="center"):
            bs.Label("A")
            bs.Label("B")
            bs.Label("C")

        with bs.GroupBox("Grid", layout="grid", columns=[1, 1], padding=10, gap=8, vertical_items="center"):
            bs.Label("Name:")
            bs.Label("Ada Lovelace")
            bs.Label("Role:")
            bs.Label("Engineer")

    # In context
    bs.Label("In Context", font="heading-sm")
    with bs.Row(gap=12):

        with bs.GroupBox("Connection", accent="primary", padding=12, gap=8):
            with bs.Row(gap=8, vertical_items="center"):
                bs.Label("Host:")
                bs.Label("localhost")
            with bs.Row(gap=8, vertical_items="center"):
                bs.Label("Port:")
                bs.Label("5432")
            with bs.Row(gap=8, vertical_items="center"):
                bs.Label("Status:")
                bs.Label("Connected", accent="success")

        with bs.GroupBox("Alerts", accent="warning", padding=12, gap=6):
            bs.Label("Disk usage above 80%", accent="warning")
            bs.Label("2 services degraded", accent="danger")
            bs.Label("Backup completed", accent="success")

app.run()