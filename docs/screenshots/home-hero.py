"""Hero screenshot for the home page — a rich, static dashboard layout.

A labeled workspace rail (sidebar hidden) reclaims width; a 4-column grid holds
three KPI cards and a searchable, paged table, with a tall "This month" panel in
the last column. Layout only: real widgets, no reactive behavior and no charts.
Captures wider than the in-page shots (the home page has no doc sidebar).

Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py home-hero
"""
import bootstack as bs

KPIS = [
    ("Revenue", "$48.2k", "+12% vs last month", "primary"),
    ("Orders", "1,204", "Target +4%", "success"),
    ("Visitors", "18.9k", "Last 30 days", "info"),
]

_NAMES = [
    "Dana Reyes", "Sam Okonkwo", "Priya Nair", "Liam Walsh", "Grace Hopper",
    "Noah Kim", "Ava Martinez", "Mateo Rossi", "Yuki Tanaka", "Owen Clarke",
    "Zara Ahmed", "Hugo Bernard", "Ines Costa", "Felix Wagner",
]
_STATUS = ["Paid", "Paid", "Pending", "Paid", "Refunded", "Pending", "Paid"]
ORDERS = [
    {
        "id": f"#{1042 - i}",
        "customer": _NAMES[i % len(_NAMES)],
        "amount": f"${(1280 + i * 137) % 4000 + 320:,}",
        "status": _STATUS[i % len(_STATUS)],
    }
    for i in range(28)
]


def _stat(label, pct, accent):
    with bs.Column(horizontal="stretch", gap=3):
        with bs.Row(horizontal="stretch"):
            bs.Label(label, font="caption", accent="secondary")
            bs.Label(f"{pct}%", font="caption", grow=True, horizontal="right")
        bs.ProgressBar(value=pct, accent=accent, horizontal="stretch")


with bs.AppShell(title="Acme Analytics", size=(890, 650),
                 rail_labels=True, show_sidebar=False, show_statusbar=True) as shell:
    shell._capture_full_window = True
    shell._capture_max_width = 940
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New report", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Export…", shortcut="Mod+E", on_click=lambda: None)
            file.add_divider()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        bar.add_button("Export", icon="download")
        bar.add_theme_toggle()

    shell.statusbar.add_text("Connected", icon="wifi")
    shell.statusbar.add_text("Synced 2 minutes ago", icon="arrow-repeat")
    shell.statusbar.add_text("v1.0.0", side="right")
    shell.statusbar.add_text("UTC-05:00", icon="clock", side="right")
    shell.statusbar.add_text("1,204 records", icon="database", side="right")

    with shell.add_workspace("dashboard", text="Dashboard", icon="speedometer2") as ws:
        with ws.content:
            with bs.Column(grow=True, horizontal="stretch", gap=12, padding=18):
                with bs.Grid(columns=4, rows=[0, 1], gap=14, grow=True, horizontal="stretch"):
                    for i, (label, value, delta, accent) in enumerate(KPIS):
                        with bs.Card(accent=accent, padding=8, gap=0, row=0, column=i):
                            bs.Label(label)
                            bs.Label(value, font="display-lg")
                            bs.Label(delta, font="caption", accent="secondary")

                    with bs.Column(row=1, column=0, columnspan=3, gap=6):
                        bs.DataTable(
                            columns=[
                                {"key": "id", "text": "Order", "width": 75},
                                {"key": "customer", "text": "Customer", "width": 170},
                                {"key": "amount", "text": "Amount", "width": 100, "anchor": "e"},
                                {"key": "status", "text": "Status", "width": 105},
                            ],
                            rows=ORDERS,
                            density="compact",
                            page_size=13,
                            grow=True, horizontal="stretch",
                        )

                    with bs.Card(row=0, column=3, rowspan=2, padding=16, gap=10):
                        bs.Label("This month", font="heading-sm")
                        _stat("Monthly goal", 72, "primary")
                        _stat("New customers", 48, "info")
                        _stat("Churn", 12, "danger")
                        with bs.Column(horizontal="stretch", horizontal_items="center", margin_y=4):
                            bs.Gauge(value=86, size=150, thickness=14, variant="semi",
                                     segment_width=4, value_suffix="%",
                                     subtitle="Satisfaction", surface="card",
                                     accent="success", margin_y=(24, 0))
                        bs.Divider(horizontal="stretch")
                        bs.Label("Refresh rate", font="caption", accent="secondary")
                        bs.Slider(value=60, min_value=0, max_value=100, horizontal="stretch")
                        bs.Switch("Auto-refresh", value=True)
                        bs.Switch("Email alerts", value=False)
                        with bs.Row(horizontal="stretch", gap=8):
                            bs.Button("Reset", variant="ghost")
                            bs.Button("Apply", accent="primary", grow=True)

    with shell.add_workspace("orders", text="Orders", icon="receipt") as ws:
        with ws.content:
            bs.Label("Orders", font="heading-lg")
    with shell.add_workspace("reports", text="Reports", icon="file-earmark-text") as ws:
        with ws.content:
            bs.Label("Reports", font="heading-lg")
    with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
        with ws.content:
            bs.Label("Settings", font="heading-lg")

shell.run()
