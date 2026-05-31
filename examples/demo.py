"""Data Analysis Workbench — bootstack hero demo.

A single-file showcase application for the bootstack homepage hero
screenshot. All data is hardcoded; button commands are no-ops. Run with:

    python examples/demo.py
"""

import bootstack as bs


# ---------------------------------------------------------------------------
# Hardcoded data
# ---------------------------------------------------------------------------

ANALYSIS_ROWS = [
    ("S-00142", "2026-05-04 09:12:03", "CH-1", "1.0432", "+0.0021", "Pass"),
    ("S-00143", "2026-05-04 09:12:18", "CH-1", "1.0438", "+0.0006", "Pass"),
    ("S-00144", "2026-05-04 09:12:33", "CH-2", "0.8821", "-0.0143", "Warning"),
    ("S-00145", "2026-05-04 09:12:48", "CH-2", "0.8794", "-0.0027", "Warning"),
    ("S-00146", "2026-05-04 09:13:03", "CH-3", "1.2104", "+0.0312", "Pass"),
    ("S-00147", "2026-05-04 09:13:18", "CH-3", "1.2098", "-0.0006", "Pass"),
    ("S-00148", "2026-05-04 09:13:33", "CH-1", "1.0451", "+0.0013", "Pass"),
    ("S-00149", "2026-05-04 09:13:48", "CH-4", "2.1583", "+0.4821", "Fail"),
    ("S-00150", "2026-05-04 09:14:03", "CH-4", "2.0012", "-0.1571", "Fail"),
    ("S-00151", "2026-05-04 09:14:18", "CH-2", "0.8902", "+0.0108", "Warning"),
    ("S-00152", "2026-05-04 09:14:33", "CH-1", "1.0445", "-0.0006", "Pass"),
    ("S-00153", "2026-05-04 09:14:48", "CH-3", "1.2112", "+0.0014", "Pass"),
    ("S-00154", "2026-05-04 09:15:03", "CH-1", "1.0429", "-0.0016", "Pass"),
    ("S-00155", "2026-05-04 09:15:18", "CH-2", "0.8867", "-0.0035", "Warning"),
    ("S-00156", "2026-05-04 09:15:33", "CH-3", "1.2105", "-0.0007", "Pass"),
]

RESULTS_ROWS = [
    ("R-1042", "Run-A12", "2026-05-04 09:12", "CH-1", "1.0438", "V", "0.0021", "23.4", "Pass"),
    ("R-1043", "Run-A12", "2026-05-04 09:12", "CH-2", "0.8794", "V", "0.0143", "23.5", "Warning"),
    ("R-1044", "Run-A12", "2026-05-04 09:13", "CH-3", "1.2104", "V", "0.0312", "23.4", "Pass"),
    ("R-1045", "Run-A12", "2026-05-04 09:13", "CH-4", "2.1583", "V", "0.4821", "23.6", "Fail"),
    ("R-1046", "Run-A13", "2026-05-04 10:02", "CH-1", "1.0451", "V", "0.0013", "22.9", "Pass"),
    ("R-1047", "Run-A13", "2026-05-04 10:02", "CH-2", "0.8902", "V", "0.0108", "22.8", "Warning"),
    ("R-1048", "Run-A13", "2026-05-04 10:03", "CH-3", "1.2112", "V", "0.0014", "22.8", "Pass"),
    ("R-1049", "Run-A13", "2026-05-04 10:03", "CH-4", "2.0012", "V", "0.1571", "22.9", "Fail"),
    ("R-1050", "Run-A14", "2026-05-04 11:18", "CH-1", "1.0429", "V", "0.0016", "23.1", "Pass"),
    ("R-1051", "Run-A14", "2026-05-04 11:18", "CH-2", "0.8867", "V", "0.0035", "23.2", "Warning"),
    ("R-1052", "Run-A14", "2026-05-04 11:19", "CH-3", "1.2105", "V", "0.0007", "23.2", "Pass"),
    ("R-1053", "Run-A14", "2026-05-04 11:19", "CH-4", "1.9874", "V", "0.0211", "23.3", "Pass"),
    ("R-1054", "Run-A15", "2026-05-04 13:44", "CH-1", "1.0440", "V", "0.0011", "23.0", "Pass"),
    ("R-1055", "Run-A15", "2026-05-04 13:44", "CH-2", "0.8881", "V", "0.0014", "23.1", "Pass"),
    ("R-1056", "Run-A15", "2026-05-04 13:45", "CH-3", "1.2098", "V", "0.0007", "23.0", "Pass"),
    ("R-1057", "Run-A15", "2026-05-04 13:45", "CH-4", "2.0123", "V", "0.0249", "23.1", "Warning"),
]

CHANNEL_STATUS = [
    ("CH-1", 100, "success", "Pass"),
    ("CH-2", 88,  "warning", "Warning"),
    ("CH-3", 100, "success", "Pass"),
    ("CH-4", 45,  "danger",  "Fail"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stat_card(label, value, color=None, big=True):
    kw = {"accent": color} if color else {}
    with bs.Card(padding=10, **kw):
        bs.Label(label, font="caption", accent="secondary")
        bs.Label(
            value,
            font="heading-md[bold]" if big else "body-lg[bold]",
            accent=color,
        )


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def _build_analysis_page():
    with bs.VStack(fill="both", expand=True, gap=12, padding=20):

        # Page header
        with bs.HStack(gap=10, anchor_items="center", fill="x", fill_items='y'):
            bs.Label("Analysis", font="heading-xl[bold]")
            bs.Label("Run-A15  ·  CH-1 through CH-4  ·  15 samples", accent="secondary")

        # Two-column main area
        with bs.Grid(columns=["380px", 1], gap=12, sticky_items="nsew", fill="x"):

            # Left: Run Parameters
            with bs.GroupBox("Run Parameters", padding=12, gap=16, fill_items='x'):
                bs.Select(
                    label="Dataset",
                    options=[
                        "calib_run_2026-05-04",
                        "calib_run_2026-05-03",
                        "field_run_2026-04-29",
                        "baseline_q1_2026",
                    ],
                    value="calib_run_2026-05-04"
                )
                with bs.HStack(gap=8, fill_items="x", expand_items=True):
                    bs.DateField(label="From", value="2026-05-13")
                    bs.DateField(label="To",   value="2026-05-15")
                with bs.VStack(gap=4, padding=(0, 8)):
                    bs.Label("Threshold Range", font="label")
                    bs.RangeSlider(
                        min_value=0.0, max_value=3.0,
                        low_value=0.5, high_value=2.0,
                        fill="x",
                        expand=True
                    )

                with bs.HStack(gap=16):
                    bs.Switch("Drop outliers",  accent="primary", value=True)
                    bs.Switch("Auto-baseline",  accent="primary", value=True)
                    bs.Switch("Normalize",       accent="primary", value=False)

                with bs.VStack(gap=4):
                    bs.Label("Channels", font="label")
                    tg = bs.ToggleGroup(mode="multi", accent="primary", variant="outline")
                    tg.add("CH-1", value="ch1")
                    tg.add("CH-2", value="ch2")
                    tg.add("CH-3", value="ch3")
                    tg.add("CH-4", value="ch4")

                with bs.HStack(gap=6, fill="x", fill_items="x", expand_items=True, anchor='s', expand=True):
                    bs.Button("Run",    icon="play-fill", accent="primary",   on_click=lambda: None)
                    bs.Button("Stop",   icon="stop-fill", accent="danger",    variant="outline", on_click=lambda: None)
                    bs.Button("Export", icon="download",  accent="secondary", variant="outline", on_click=lambda: None)

            # Right: Summary Statistics + Run Status
            with bs.VStack(gap=12):

                with bs.GroupBox("Summary Statistics", padding=12, gap=8, fill="x"):
                    with bs.Grid(gap=8, columns=4, sticky_items="nsew", fill='x'):
                        _stat_card("Min",    "0.8794", "success")
                        _stat_card("Max",    "2.1583", "success")
                        _stat_card("Mean",   "1.2543", "primary")
                        _stat_card("StdDev", "0.4127", "primary")
                        _stat_card("Samples",  "15", big=False)
                        _stat_card("Channels", "4",  big=False)
                        _stat_card("Outliers", "2",  "warning", big=False)
                        _stat_card("Failed",   "2",  "danger",  big=False)

                with bs.GroupBox("Run Status", padding=16, fill="x"):
                    with bs.HStack(gap=20, fill="x"):
                        bs.Gauge(
                            value=78, max_value=100,
                            subtitle="Complete",
                            accent="success",
                            interactive=False,
                        )
                        with bs.VStack(gap=10, fill="both", expand=True):
                            with bs.HStack(gap=20):
                                with bs.VStack(anchor_items="w"):
                                    bs.Label("State",    font="caption", accent="secondary")
                                    bs.Badge("Complete", accent="success", variant="pill")
                                with bs.VStack(anchor_items="w"):
                                    bs.Label("Elapsed", font="caption", accent="secondary")
                                    bs.Label("0:00:42", font="heading-sm[bold]")
                                with bs.VStack(anchor_items="w"):
                                    bs.Label("Started",  font="caption", accent="secondary")
                                    bs.Label("13:44:15", font="body[bold]")

                            bs.Separator(fill="x")

                            bs.Label("Channel Status", font="caption", accent="secondary")
                            for ch_id, pct, color, status in CHANNEL_STATUS:
                                with bs.HStack(gap=8, anchor_items="center", fill="x"):
                                    bs.Label(ch_id, font="caption", width=5)
                                    bs.ProgressBar(
                                        value=pct, max_value=100,
                                        accent=color,
                                        fill="x", expand=True,
                                    )
                                    bs.Label(status, font="caption", accent=color, width=8)

        # Sample Readings table
        with bs.GroupBox("Sample Readings", padding=8, fill="both", expand=True):
            cols = ["sample", "ts", "channel", "value", "delta", "status"]
            tree = bs.Tree(columns=cols, show="headings", height=7, fill="both", expand=True)
            tree.heading("sample",  text="Sample ID")
            tree.heading("ts",      text="Timestamp")
            tree.heading("channel", text="Channel")
            tree.heading("value",   text="Value")
            tree.heading("delta",   text="Delta")
            tree.heading("status",  text="Status")
            tree.column("sample",  width=110, anchor="w")
            tree.column("ts",      width=180, anchor="w")
            tree.column("channel", width=90,  anchor="center")
            tree.column("value",   width=110, anchor="e")
            tree.column("delta",   width=110, anchor="e")
            tree.column("status",  width=110, anchor="center")
            for row in ANALYSIS_ROWS:
                tree.insert("", "end", values=row)
            tree.selection_set(tree.get_children()[0])


def _build_results_page():
    with bs.VStack(fill="both", expand=True, gap=12, padding=20):

        with bs.HStack(gap=10, anchor_items="s", fill="x"):
            bs.Label("Results", font="heading-xl[bold]")
            bs.Label("Cross-run readings  ·  filtered & exportable", accent="secondary")

        with bs.GroupBox("Filters", padding=12, fill="x"):
            with bs.HStack(gap=8, fill="x"):
                bs.TextField(
                    label="Search", message="Sample ID, run, channel…",
                    fill="x", expand=True,
                )
                bs.Select(
                    label="Status",
                    options=["All", "Pass", "Warning", "Fail"],
                    value="All",
                )
                bs.DateField(label="Date")
                bs.Button("Refresh", icon="arrow-clockwise", accent="primary", on_click=lambda: None)

        with bs.GroupBox("Readings", padding=8, fill="both", expand=True):
            cols = ["id", "run", "timestamp", "channel", "reading", "unit", "delta", "temp", "status"]
            tree = bs.Tree(columns=cols, show="headings", height=10, fill="both", expand=True)
            tree.heading("id",        text="ID")
            tree.heading("run",       text="Run")
            tree.heading("timestamp", text="Timestamp")
            tree.heading("channel",   text="Channel")
            tree.heading("reading",   text="Reading")
            tree.heading("unit",      text="Unit")
            tree.heading("delta",     text="|Δ|")
            tree.heading("temp",      text="Temp °C")
            tree.heading("status",    text="Status")
            tree.column("id",        width=90)
            tree.column("run",       width=100)
            tree.column("timestamp", width=150)
            tree.column("channel",   width=80,  anchor="center")
            tree.column("reading",   width=100, anchor="e")
            tree.column("unit",      width=60,  anchor="center")
            tree.column("delta",     width=90,  anchor="e")
            tree.column("temp",      width=90,  anchor="e")
            tree.column("status",    width=110, anchor="center")
            for row in RESULTS_ROWS:
                tree.insert("", "end", values=row)

        with bs.Grid(columns=[1, "auto"], fill="x"):
            bs.Label(f"{len(RESULTS_ROWS)} records", accent="secondary")
            bs.Button(
                "Export", icon="download", accent="secondary",
                variant="outline", on_click=lambda: None,
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    with bs.AppShell(
        title="Data Analysis Workbench",
        minsize=(1200, 780),
    ) as shell:
        shell.toolbar.add_button(icon="sun",  command=bs.toggle_theme)
        shell.toolbar.add_button(icon="gear", command=lambda: None)

        with shell.add_page("analysis", text="Analysis", icon="bar-chart-line"):
            _build_analysis_page()

        with shell.add_page("results", text="Results", icon="table"):
            _build_results_page()

        shell.add_page("reports",  text="Reports",  icon="file-earmark-text")
        shell.add_page("settings", text="Settings", icon="gear")

        shell.navigate("analysis")

    shell.run()


if __name__ == "__main__":
    main()
