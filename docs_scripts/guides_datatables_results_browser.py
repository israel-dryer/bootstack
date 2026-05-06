import bootstack as bs
from bootstack.constants import BOTH, LEFT, RIGHT, X, YES, N

RESULTS = [
    ("R-1042", "Run-A12", "2026-05-04 09:12", "CH-1", "1.0438", "V", "0.0021", "23.4", "Pass"),
    ("R-1043", "Run-A12", "2026-05-04 09:12", "CH-2", "0.8794", "V", "0.0143", "23.5", "Warning"),
    ("R-1044", "Run-A12", "2026-05-04 09:13", "CH-3", "1.2104", "V", "0.0312", "23.4", "Pass"),
    ("R-1045", "Run-A12", "2026-05-04 09:13", "CH-4", "2.1583", "V", "0.4821", "23.6", "Fail"),
    ("R-1046", "Run-A13", "2026-05-04 10:02", "CH-1", "1.0451", "V", "0.0013", "22.9", "Pass"),
    ("R-1047", "Run-A13", "2026-05-04 10:02", "CH-2", "0.8902", "V", "0.0108", "22.8", "Warning"),
]

COLUMNS = [
    {"text": "ID",        "key": "run_id",  "width": 90},
    {"text": "Run",       "key": "run",     "width": 100},
    {"text": "Timestamp", "key": "ts",      "width": 150},
    {"text": "Channel",   "key": "channel", "width": 80,  "anchor": "center"},
    {"text": "Reading",   "key": "reading", "width": 100, "anchor": "e"},
    {"text": "Unit",      "key": "unit",    "width": 60,  "anchor": "center"},
    {"text": "|Δ|",       "key": "delta",   "width": 90,  "anchor": "e"},
    {"text": "Temp °C",   "key": "temp",    "width": 90,  "anchor": "e"},
    {"text": "Status",    "key": "status",  "width": 110, "anchor": "center", "stretch": True},
]

app = bs.App(title="Results", minsize=(1100, 540))

# --- Filter toolbar ---------------------------------------------------------
filters = bs.LabelFrame(app, text="Filters", padding=12)
filters.pack(fill=X, padx=20, pady=(20, 12))

fbar = bs.PackFrame(filters, direction="horizontal", gap=8, anchor_items=N)
fbar.pack(fill=X)

search = bs.TextEntry(fbar, label="Search", message="Sample ID, run, channel…")
search.pack(fill=X, expand=YES)

status = bs.SelectBox(
    fbar, label="Status",
    items=["All", "Pass", "Warning", "Fail"], value="All",
)
status.pack()

# --- Table ------------------------------------------------------------------
table_frame = bs.LabelFrame(app, text="Readings", padding=10)
table_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 8))

tv = bs.TableView(
    table_frame,
    columns=COLUMNS,
    rows=RESULTS,
    striped=True,
    enable_filtering=False,    # use external filter toolbar instead
    enable_search=False,
    show_table_status=False,
    page_size=len(RESULTS),
)
tv.pack(fill=BOTH, expand=YES)

# --- Apply external filters --------------------------------------------------
def apply_filters(_evt=None):
    clauses = []
    if (q := search.get().strip()):
        q = q.replace("'", "''")
        clauses.append(
            f"(run_id LIKE '%{q}%' OR run LIKE '%{q}%' OR channel LIKE '%{q}%')"
        )
    if (s := status.get()) and s != "All":
        clauses.append(f"status = '{s}'")
    tv.set_filters(" AND ".join(clauses) if clauses else "")

search.on_input(apply_filters)
status.bind("<<Change>>", apply_filters, add=True)

# --- Footer -----------------------------------------------------------------
footer = bs.Frame(app)
footer.pack(fill=X, padx=20, pady=(0, 20))
bs.Label(
    footer, text=f"{len(RESULTS)} records", font="body", accent="secondary",
).pack(side=LEFT)
bs.Button(
    footer, text="Export", icon="download", accent="secondary",
    variant="outline", command=lambda: None,
).pack(side=RIGHT)

app.mainloop()