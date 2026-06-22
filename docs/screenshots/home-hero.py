"""Hero screenshot for the home page — a modern analytics dashboard.

A labeled workspace rail (sidebar hidden) reclaims width; a header with period
controls, a row of KPI cards with trend badges, a multi-series sales **chart**
beside a "Today's Performance" list, and a recent-transactions table. Real
widgets, static data. Captures wider than the in-page shots (the home page has
no doc sidebar).

Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py home-hero
"""
import math
from pathlib import Path

import bootstack as bs

_AVATAR = Path(__file__).parent.parent / "_static" / "examples" / "avatar-profile.jpg"

# (icon, label, value, change, trend-accent)
KPIS = [
    ("coin", "Total Revenue", "$24,580", "+12.5%", "success"),
    ("receipt", "Transactions", "542", "+8.2%", "success"),
    ("bag", "Avg Order Value", "$45.32", "+5.1%", "success"),
    ("people", "Active Users", "2,482", "-2.4%", "danger"),
]

_HOURS = ["10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm"]


def sales_chart(ax):
    """Layered area chart — translucent accent fills under smooth lines."""
    from matplotlib.ticker import FuncFormatter

    n = len(_HOURS)

    def s1(x):
        return 11 + 4 * math.sin(0.9 * x + 0.3) + 2 * math.cos(1.6 * x)

    def s2(x):  # kept lower so the two areas layer cleanly
        return 7.5 + 3.2 * math.sin(0.75 * x + 1.8) + 1.3 * math.cos(1.2 * x + 0.5)

    x = [i / 12 for i in range(12 * (n - 1) + 1)]
    y1, y2 = [s1(t) for t in x], [s2(t) for t in x]
    c1, = ax.plot(x, y1, linewidth=2, label="Sales")
    ax.fill_between(x, y1, color=c1.get_color(), alpha=0.22)
    c2, = ax.plot(x, y2, linewidth=2, label="Transactions")
    ax.fill_between(x, y2, color=c2.get_color(), alpha=0.22)

    ax.set_xticks(list(range(n)))
    ax.set_xticklabels(_HOURS)
    ax.set_ylim(0, 20)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}k" if v else "0"))
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False)
    ax.margins(x=0.02)


TXNS = [
    {"id": "TXN-001", "time": "2:47pm", "amount": "$128.50", "items": "5 items",
     "payment": "Card", "cashier": "John", "status": "Completed"},
    {"id": "TXN-002", "time": "2:44pm", "amount": "$54.20", "items": "2 items",
     "payment": "Cash", "cashier": "Priya", "status": "Completed"},
    {"id": "TXN-003", "time": "2:41pm", "amount": "$312.00", "items": "9 items",
     "payment": "Card", "cashier": "Sam", "status": "Pending"},
    {"id": "TXN-004", "time": "2:38pm", "amount": "$76.40", "items": "3 items",
     "payment": "Card", "cashier": "Dana", "status": "Completed"},
    {"id": "TXN-005", "time": "2:35pm", "amount": "$219.90", "items": "7 items",
     "payment": "Mobile", "cashier": "John", "status": "Completed"},
    {"id": "TXN-006", "time": "2:33pm", "amount": "$18.75", "items": "1 item",
     "payment": "Cash", "cashier": "Priya", "status": "Refunded"},
    {"id": "TXN-007", "time": "2:29pm", "amount": "$143.20", "items": "6 items",
     "payment": "Card", "cashier": "Sam", "status": "Completed"},
    {"id": "TXN-008", "time": "2:25pm", "amount": "$402.10", "items": "12 items",
     "payment": "Card", "cashier": "Dana", "status": "Completed"},
    {"id": "TXN-009", "time": "2:22pm", "amount": "$67.00", "items": "2 items",
     "payment": "Mobile", "cashier": "John", "status": "Pending"},
    {"id": "TXN-010", "time": "2:19pm", "amount": "$95.30", "items": "4 items",
     "payment": "Cash", "cashier": "Priya", "status": "Completed"},
]


def _kpi(icon, label, value, change, accent):
    with bs.Card(grow=True, horizontal="stretch", horizontal_items="left", padding=8):
        with bs.Row(gap=8, vertical_items="center"):
            bs.Label(icon=icon, accent=accent)
            bs.Label(label, font="caption", accent="secondary")
        bs.Divider(horizontal="stretch", margin_y=4)
        with bs.Row(vertical_items="center", margin_y=(8, 0)):
            bs.Label(value, font="heading-xl")
            bs.Badge(change, accent=f"{accent}[subtle]")
        bs.Label("vs last period", font="caption", accent="secondary")


with bs.AppShell(title="Acme POS", size=(890, 720), show_statusbar=True,
                 sidebar_mode="compact") as shell:
    shell._capture_full_window = True
    shell._capture_max_width = 940
    with shell.add_toolbar(padding=(10, 3)) as bar:
        bar.add_label("POS Dashboard", icon="boxes", font="heading-sm")
        bar.add_spacer()
        bar.add_button(icon="bell")
        bar.add_theme_toggle()
        bar.add_widget(bs.Avatar, image=_AVATAR, size=24)

    shell.statusbar.add_text("Connected", icon="wifi")
    shell.statusbar.add_text("Synced 2 minutes ago", icon="arrow-repeat")
    shell.statusbar.add_text("v1.0.0", side="right")
    shell.statusbar.add_text("2,482 active users", icon="people", side="right")

    with shell.page_nav() as nav:
        with nav.add_page("dashboard", text="Dashboard", icon="speedometer2", padding=0):
            with bs.ScrollView(grow=True, horizontal="stretch"):
                with bs.Column(horizontal="stretch", gap=12, padding=18):
                    # Header — title, subtitle, period controls.
                    with bs.Row(horizontal="stretch", vertical_items="center"):
                        with bs.Column(gap=0, horizontal_items="left"):
                            bs.Label("Overview", font="heading-lg")
                            bs.Label("Real-time sales and performance metrics",
                                     font="caption", accent="secondary")
                        bs.Spacer()
                        bs.SelectButton(["Last 24 hours"], value="Last 24 hours", icon="calendar3", variant="outline", density="compact")
                        bs.Button("Expert", icon="stars", accent="primary", density="compact")

                    # KPI cards.
                    with bs.Grid(horizontal="stretch", columns=4, gap=12):
                        for icon, label, value, change, accent in KPIS:
                            _kpi(icon, label, value, change, accent)

                    # Main — the sales chart beside the performance list.
                    with bs.Grid(horizontal="stretch", vertical_items="stretch", gap=14, columns=4):
                        with bs.Card(grow=True, horizontal="stretch", horizontal_items="left", columnspan=3):
                            bs.Label("Sales and Transactions", font="heading-sm")
                            bs.Label("Hourly sales and transaction volume", font="caption", accent="secondary")
                            with bs.Column(height=150, horizontal="stretch", grow=True, margin_y=(8, 0)):
                                bs.Chart(render=sales_chart, grow=True, horizontal="stretch")

                        with bs.Card(padding=16, gap=8, horizontal="stretch", grow=1):
                            bs.Label("Options", font="heading-sm", horizontal="left")
                            with bs.Column(horizontal="stretch", horizontal_items="stretch", gap=12):

                                bs.Switch("Email alerts", horizontal="left")
                                bs.Switch("Auto-refresh", value=True, horizontal="left")
                                bs.Slider(value=75, horizontal="stretch", show_minmax=True, tick_step=25)
                                bs.Button("Apply", density="compact", icon="sliders")


                    # Recent transactions.
                    with bs.Card(padding=16, gap=8, horizontal="stretch"):
                        bs.Label("Recent Transactions", font="heading-sm", horizontal="left")
                        bs.DataTable(
                            columns=[
                                {"key": "id", "text": "Transaction ID", "width": 140},
                                {"key": "time", "text": "Time", "width": 80},
                                {"key": "amount", "text": "Amount", "width": 95, "anchor": "e"},
                                {"key": "items", "text": "Items", "width": 85},
                                {"key": "payment", "text": "Payment", "width": 100},
                                {"key": "cashier", "text": "Cashier", "width": 100},
                                {"key": "status", "text": "Status", "width": 110},
                            ],
                            rows=TXNS,
                            density="compact",
                            searchable=False,
                            paginated=False,
                            horizontal="stretch",
                        )

        with nav.add_page("sales", text="Sales", icon="cart3"):
            bs.Label("Sales", font="heading-lg")
        with nav.add_page("analytics", text="Analytics", icon="graph-up-arrow"):
            bs.Label("Analytics", font="heading-lg")
        with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True):
            bs.Label("Settings", font="heading-lg")

    shell.navigate("dashboard")

shell.run()
