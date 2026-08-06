"""Visual check for the group-header fixes shipping in 0.2.2.

Covers all four issues in one window:

  #417  on_row_double_click must fire on a READ-ONLY table
  #418  right-click on a group header must NOT fire on_row_right_click
  #419  a group header's chevron must match its open/closed state
  #420  double-click on a group header must not fire a row event, and must not
        open a "New Record" dialog on the editable table

The two panels are the same data with the only difference being `allow_edit`,
because several of these defects were reachable on one and not the other.

The status line under each table is the thing to watch for #419: it reports the
group's real open state next to what its chevron is drawing. They must agree
after every interaction. Run it, then work through the checklist printed in the
window.

    py -3.13 development/demo_419_group_chevrons.py
"""
import bootstack as bs
from bootstack.scheduling import Schedule

ROWS = [
    {"id": 1, "name": "Ada", "role": "eng"},
    {"id": 2, "name": "Grace", "role": "eng"},
    {"id": 3, "name": "Boole", "role": "math"},
    {"id": 4, "name": "Church", "role": "math"},
    {"id": 5, "name": "Cy", "role": "ops"},
]
COLUMNS = ["id", "name", "role"]

CHECKLIST = (
    "1.  Click a group header — it collapses, chevron follows.  (baseline)\n"
    "2.  Click it again — it expands, chevron follows.\n"
    "3.  Click a DATA row (not a header — a header click does not take focus),\n"
    "    then Up/Down onto a group header. Collapse it with Left, then expand\n"
    "    with Space, Enter and Right — the chevron must follow all three.     (#419)\n"
    "4.  Double-click a group header — chevron must still agree; no dialog.    (#419/#420)\n"
    "5.  Double-click a DATA row on the left panel — the log shows an event.   (#417)\n"
    "6.  Right-click a group header — the log must stay silent.                (#418)\n"
    "7.  Double-click a data row on the right panel — Edit Record opens, and\n"
    "    it is titled 'Edit Record', never 'New Record'.                       (#420)"
)


def build_panel(title, *, allow_edit):
    """One titled table panel; returns (table, status_label)."""
    with bs.Column(gap=6, grow=1):
        bs.Label(title, font="heading-md")
        table = bs.DataTable(rows=[dict(r) for r in ROWS], columns=COLUMNS,
                             allow_edit=allow_edit, grow=1)
        status = bs.Label("—", font="code")
    table.group_by("role")
    return table, status


def chevron_report(table):
    """Per-group 'state vs chevron' readout, flagged when the two disagree."""
    impl = table._internal
    open_icon = str(impl._chevron_icon(True))
    parts = []
    for key, iid in impl._group_parents.items():
        opened = bool(int(impl._tree.item(iid, "open") or 0))
        image = impl._tree.item(iid, "image")
        if isinstance(image, (list, tuple)):
            image = image[0] if image else ""
        drawn_open = str(image) == open_icon
        flag = "  ok" if opened == drawn_open else "  <-- MISMATCH"
        parts.append(f"{key}: state={'open  ' if opened else 'closed'} "
                     f"chevron={'open  ' if drawn_open else 'closed'}{flag}")
    return "\n".join(parts) or "—"


with bs.App(title="0.2.2 group-header checks (#417 #418 #419 #420)",
            size=(1000, 760), padding=14, gap=10) as app:
    bs.Label("Group header behavior — 0.2.2 verification", font="heading-lg")
    bs.Label(CHECKLIST, font="code")
    bs.Divider()

    with bs.Row(gap=16, grow=1):
        read_only, ro_status = build_panel("Read-only  (default)", allow_edit=False)
        editable, ed_status = build_panel("allow_edit=True", allow_edit=True)

    bs.Divider()
    bs.Label("Row events  (a group header must never appear here)", font="heading-md")
    event_log = bs.Label("no row events yet", font="code")

log_lines = []


def log(source, kind, event):
    record = getattr(event, "record", None)
    empty = " <-- EMPTY RECORD, should not happen" if record == {} else ""
    log_lines.append(f"{source:9s} {kind:12s} record={record} id={getattr(event, 'id', None)}{empty}")
    event_log.text = "\n".join(log_lines[-6:])


for label, table in (("read-only", read_only), ("editable", editable)):
    table.on_row_double_click(lambda e, s=label: log(s, "double-click", e))
    table.on_row_right_click(lambda e, s=label: log(s, "right-click", e))

schedule = Schedule(app)


def refresh():
    ro_status.text = chevron_report(read_only)
    ed_status.text = chevron_report(editable)


schedule.every(150, refresh)
app.run()
