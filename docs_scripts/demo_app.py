"""Data Analysis Workbench — bootstack hero demo.

A single-file showcase application used for the bootstack homepage hero
screenshot. All data is hardcoded; button commands are no-ops. Run with:

    python docs_scripts/demo_app.py
"""

import bootstack as bs
from bootstack.constants import (
    BOTH, CENTER, END, HORIZONTAL, LEFT, RIGHT, W, X, Y, YES,
)


# ---------------------------------------------------------------------------
# Hardcoded fake data
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
    ("R-1042", "Run-A12", "2026-05-04 09:12", "CH-1", "1.0438", "V",  "0.0021", "23.4", "Pass"),
    ("R-1043", "Run-A12", "2026-05-04 09:12", "CH-2", "0.8794", "V",  "0.0143", "23.5", "Warning"),
    ("R-1044", "Run-A12", "2026-05-04 09:13", "CH-3", "1.2104", "V",  "0.0312", "23.4", "Pass"),
    ("R-1045", "Run-A12", "2026-05-04 09:13", "CH-4", "2.1583", "V",  "0.4821", "23.6", "Fail"),
    ("R-1046", "Run-A13", "2026-05-04 10:02", "CH-1", "1.0451", "V",  "0.0013", "22.9", "Pass"),
    ("R-1047", "Run-A13", "2026-05-04 10:02", "CH-2", "0.8902", "V",  "0.0108", "22.8", "Warning"),
    ("R-1048", "Run-A13", "2026-05-04 10:03", "CH-3", "1.2112", "V",  "0.0014", "22.8", "Pass"),
    ("R-1049", "Run-A13", "2026-05-04 10:03", "CH-4", "2.0012", "V",  "0.1571", "22.9", "Fail"),
    ("R-1050", "Run-A14", "2026-05-04 11:18", "CH-1", "1.0429", "V",  "0.0016", "23.1", "Pass"),
    ("R-1051", "Run-A14", "2026-05-04 11:18", "CH-2", "0.8867", "V",  "0.0035", "23.2", "Warning"),
    ("R-1052", "Run-A14", "2026-05-04 11:19", "CH-3", "1.2105", "V",  "0.0007", "23.2", "Pass"),
    ("R-1053", "Run-A14", "2026-05-04 11:19", "CH-4", "1.9874", "V",  "0.0211", "23.3", "Pass"),
    ("R-1054", "Run-A15", "2026-05-04 13:44", "CH-1", "1.0440", "V",  "0.0011", "23.0", "Pass"),
    ("R-1055", "Run-A15", "2026-05-04 13:44", "CH-2", "0.8881", "V",  "0.0014", "23.1", "Pass"),
    ("R-1056", "Run-A15", "2026-05-04 13:45", "CH-3", "1.2098", "V",  "0.0007", "23.0", "Pass"),
    ("R-1057", "Run-A15", "2026-05-04 13:45", "CH-4", "2.0123", "V",  "0.0249", "23.1", "Warning"),
]

STATUS_ACCENTS = {"Pass": "success", "Warning": "warning", "Fail": "danger"}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def build_analysis_page(page):
    """Main working view: parameters | summary, meter, status; data table below."""
    # Page header
    header = bs.Frame(page)
    header.pack(fill=X, padx=20, pady=(16, 4))
    bs.Label(header, text="Analysis", font="heading-xl[bold]").pack(side=LEFT)
    bs.Label(
        header,
        text="Run-A15  ·  CH-1 through CH-4  ·  15 samples",
        font="body",
        accent="secondary",
    ).pack(side=LEFT, padx=(16, 0), pady=(8, 0))

    # Top row: parameters (left, fixed) | summary + status (right, expands)
    top = bs.GridFrame(
        page, columns=["360px", 1], gap=(12, 0), sticky_items="nsew",
    )
    top.pack(fill=X, padx=20, pady=(4, 10))

    # --- Parameters card ---------------------------------------------------
    params = bs.LabelFrame(top, text="Run Parameters", padding=12)
    params.grid()

    bs.SelectBox(
        params,
        label="Dataset",
        items=[
            "calib_run_2026-05-04",
            "calib_run_2026-05-03",
            "field_run_2026-04-29",
            "baseline_q1_2026",
        ],
        value="calib_run_2026-05-04",
    ).pack(fill=X, pady=(0, 6))

    date_row = bs.PackFrame(
        params, direction="horizontal", gap=6,
        fill_items="x", expand_items=True,
    )
    date_row.pack(fill=X, pady=(0, 6))
    bs.DateEntry(date_row, label="From").pack()
    bs.DateEntry(date_row, label="To").pack()

    thresh_row = bs.PackFrame(
        params, direction="horizontal", gap=6,
        fill_items="x", expand_items=True,
    )
    thresh_row.pack(fill=X, pady=(0, 8))
    bs.NumericEntry(thresh_row, label="Min", value=0.5, increment=0.01).pack()
    bs.NumericEntry(thresh_row, label="Max", value=2.0, increment=0.01).pack()

    opts = bs.PackFrame(params, direction="vertical", gap=2, anchor_items="w")
    opts.pack(fill=X, pady=(0, 4))
    cb1 = bs.CheckButton(opts, text="Drop outliers", accent="primary")
    cb1.pack()
    cb1.invoke()
    cb2 = bs.CheckButton(opts, text="Auto-baseline correction", accent="primary")
    cb2.pack()
    cb2.invoke()

    bs.Separator(params).pack(fill=X, pady=8)

    btn_row = bs.PackFrame(
        params, direction="horizontal", gap=6,
        fill_items="x", expand_items=True,
    )
    btn_row.pack(fill=X)
    bs.Button(
        btn_row, text="Run", icon="play-fill", accent="primary",
        command=lambda: None,
    ).pack()
    bs.Button(
        btn_row, text="Stop", icon="stop-fill", accent="danger",
        variant="outline", command=lambda: None,
    ).pack()
    bs.Button(
        btn_row, text="Export", icon="download", accent="secondary",
        variant="outline", command=lambda: None,
    ).pack()

    # --- Right column: summary stacked above run-status --------------------
    right = bs.PackFrame(top, direction="vertical", gap=10)
    right.grid()

    # Summary stats card (full width of right column)
    summary = bs.LabelFrame(right, text="Summary Statistics", padding=14)
    summary.pack(fill=X)

    def _stat_cell(parent, label, value, color=None, big=True):
        cell = bs.Frame(parent)
        bs.Label(cell, text=label, font="caption", accent="secondary").pack(anchor=W)
        bs.Label(
            cell, text=value,
            font="heading-lg[bold]" if big else "body-xl[bold]",
            accent=color,
        ).pack(anchor=W, pady=(2, 0))
        return cell

    row1 = bs.PackFrame(summary, direction="horizontal", gap=18)
    row1.pack(fill=X, pady=(0, 8))
    for label, value, color in [
        ("Min",    "0.8794", "info"),
        ("Max",    "2.1583", "info"),
        ("Mean",   "1.2543", "primary"),
        ("StdDev", "0.4127", "primary"),
    ]:
        _stat_cell(row1, label, value, color, big=True).pack()

    bs.Separator(summary).pack(fill=X, pady=4)

    row2 = bs.PackFrame(summary, direction="horizontal", gap=18)
    row2.pack(fill=X, pady=(8, 0))
    for label, value, color in [
        ("Samples",  "15",  None),
        ("Channels", "4",   None),
        ("Outliers", "2",   "warning"),
        ("Failed",   "2",   "danger"),
    ]:
        _stat_cell(row2, label, value, color, big=False).pack()

    # Status / progress card — meter on left, info on right
    status_card = bs.LabelFrame(right, text="Run Status", padding=14)
    status_card.pack(fill=BOTH, expand=YES)

    status_inner = bs.PackFrame(status_card, direction="horizontal", gap=18)
    status_inner.pack(fill=X)

    bs.Meter(
        status_inner,
        size=150,
        value=78,
        maxvalue=100,
        subtitle="Complete",
        value_suffix="%",
        accent="success",
        interactive=False,
    ).pack()

    info = bs.PackFrame(status_inner, direction="vertical", gap=10)
    info.pack(fill=BOTH, expand=YES, anchor="w", pady=(8, 0))

    state_row = bs.Frame(info)
    state_row.pack(anchor=W)
    bs.Label(state_row, text="State", font="caption", accent="secondary").pack(anchor=W)
    bs.Badge(state_row, text="Complete", accent="success", variant="pill").pack(anchor=W, pady=(4, 0))

    eta_block = bs.Frame(info)
    eta_block.pack(anchor=W)
    bs.Label(eta_block, text="Elapsed", font="caption", accent="secondary").pack(anchor=W)
    bs.Label(eta_block, text="0:00:42", font="heading-md[bold]").pack(anchor=W)

    started_block = bs.Frame(info)
    started_block.pack(anchor=W)
    bs.Label(started_block, text="Started", font="caption", accent="secondary").pack(anchor=W)
    bs.Label(started_block, text="13:44:15", font="body[bold]").pack(anchor=W)

    # --- Data table (TreeView for compact, no pager) -----------------------
    table_frame = bs.LabelFrame(page, text="Sample Readings", padding=8)
    table_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 16))

    cols = ("sample", "ts", "channel", "value", "delta", "status")
    tree = bs.TreeView(table_frame, columns=cols, show="headings", height=7)
    tree.heading("sample",  text="Sample ID")
    tree.heading("ts",      text="Timestamp")
    tree.heading("channel", text="Channel")
    tree.heading("value",   text="Value")
    tree.heading("delta",   text="Delta")
    tree.heading("status",  text="Status")
    tree.column("sample",  width=110, anchor=W)
    tree.column("ts",      width=180, anchor=W)
    tree.column("channel", width=90,  anchor=CENTER)
    tree.column("value",   width=110, anchor="e")
    tree.column("delta",   width=110, anchor="e")
    tree.column("status",  width=110, anchor=CENTER)
    for row in ANALYSIS_ROWS:
        tag = row[5].lower()
        tree.insert("", END, values=row, tags=(tag,))
    tree.pack(fill=BOTH, expand=YES)
    tree.selection_set(tree.get_children()[0])


def build_results_page(page):
    """Wide tabular results view with filter row and footer."""
    header = bs.Frame(page)
    header.pack(fill=X, padx=20, pady=(20, 8))
    bs.Label(header, text="Results", font="heading-xl[bold]").pack(side=LEFT)
    bs.Label(
        header,
        text="Cross-run readings  ·  filtered & exportable",
        font="body",
        accent="secondary",
    ).pack(side=LEFT, padx=(16, 0), pady=(8, 0))

    # Filter toolbar
    filters = bs.LabelFrame(page, text="Filters", padding=12)
    filters.pack(fill=X, padx=20, pady=(4, 12))

    fbar = bs.PackFrame(filters, direction="horizontal", gap=8)
    fbar.pack(fill=X)

    bs.TextEntry(
        fbar, label="Search", message="Sample ID, run, channel…",
    ).pack(fill=X, expand=YES)

    bs.SelectBox(
        fbar, label="Status",
        items=["All", "Pass", "Warning", "Fail"], value="All",
    ).pack()

    bs.DateEntry(fbar, label="Date").pack()

    bs.Button(
        fbar, text="Refresh", icon="arrow-clockwise", accent="primary",
        command=lambda: None,
    ).pack(pady=(18, 0))

    # Results table
    table_frame = bs.LabelFrame(page, text="Readings", padding=10)
    table_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 8))

    bs.TableView(
        table_frame,
        columns=[
            {"text": "ID",        "width": 90},
            {"text": "Run",       "width": 100},
            {"text": "Timestamp", "width": 150},
            {"text": "Channel",   "width": 80,  "anchor": "center"},
            {"text": "Reading",   "width": 100, "anchor": "e"},
            {"text": "Unit",      "width": 60,  "anchor": "center"},
            {"text": "|Δ|",       "width": 90,  "anchor": "e"},
            {"text": "Temp °C",   "width": 90,  "anchor": "e"},
            {"text": "Status",    "width": 110, "anchor": "center", "stretch": True},
        ],
        rows=RESULTS_ROWS,
        striped=True,
        enable_filtering=False,
        enable_search=False,
        show_table_status=False,
        page_size=16,
    ).pack(fill=BOTH, expand=YES)

    # Footer
    footer = bs.Frame(page)
    footer.pack(fill=X, padx=20, pady=(0, 20))
    bs.Label(
        footer, text=f"{len(RESULTS_ROWS)} records",
        font="body", accent="secondary",
    ).pack(side=LEFT)
    bs.Button(
        footer, text="Export", icon="download", accent="secondary",
        variant="outline", command=lambda: None,
    ).pack(side=RIGHT)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    shell = bs.AppShell(
        title="Data Analysis Workbench",
        theme="bootstrap-light",
        minsize=(1200, 780),
    )

    # Toolbar buttons
    shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)
    shell.toolbar.add_button(icon="gear", command=lambda: None)

    # Sidebar pages — Analysis and Results are populated; the others are stubs
    analysis = shell.add_page("analysis", text="Analysis", icon="bar-chart-line")
    build_analysis_page(analysis)

    results = shell.add_page("results", text="Results", icon="table")
    build_results_page(results)

    shell.add_page("reports", text="Reports", icon="file-earmark-text")
    shell.add_page("settings", text="Settings", icon="gear")

    shell.navigate("analysis")
    shell.mainloop()


if __name__ == "__main__":
    main()
