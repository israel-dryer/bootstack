import bootstack as bs

# Column definitions — each dict maps a display label to a record key.
COLUMNS = [
    {"text": "Name", "key": "name", "width": 160},
    {"text": "Department", "key": "department", "width": 130},
    {"text": "Role", "key": "role", "width": 150},
    {"text": "Location", "key": "location", "width": 120},
    {"text": "Salary", "key": "salary", "width": 100},
    {"text": "Start Date", "key": "start_date", "width": 110},
]

_DEPARTMENTS = [
    ("Engineering", "Software Engineer"),
    ("Engineering", "Staff Engineer"),
    ("Design", "Product Designer"),
    ("Sales", "Account Executive"),
    ("Sales", "Sales Manager"),
    ("Support", "Support Specialist"),
    ("Marketing", "Content Strategist"),
]
_LOCATIONS = ["New York", "London", "Berlin", "Remote", "Tokyo"]
_NAMES = [
    "Ada Lovelace", "Alan Turing", "Grace Hopper", "Linus Torvalds",
    "Margaret Hamilton", "Dennis Ritchie", "Barbara Liskov", "Ken Thompson",
    "Katherine Johnson", "Donald Knuth", "Radia Perlman", "Brian Kernighan",
    "Hedy Lamarr", "Tim Berners-Lee", "Anita Borg", "Guido van Rossum",
    "Joan Clarke", "Vint Cerf", "Karen Spärck Jones", "James Gosling",
    "Shafi Goldwasser", "Bjarne Stroustrup", "Frances Allen", "John Carmack",
]

# Build a sample dataset large enough to page through (page_size below is 10).
ROWS = []
for i, person in enumerate(_NAMES):
    dept, role = _DEPARTMENTS[i % len(_DEPARTMENTS)]
    ROWS.append({
        "name": person,
        "department": dept,
        "role": role,
        "location": _LOCATIONS[i % len(_LOCATIONS)],
        "salary": 70_000 + (i * 4_500),
        "start_date": f"20{15 + (i % 9):02d}-{1 + (i % 12):02d}-{1 + (i % 28):02d}",
    })


with bs.App(title="Data Table Demo", size=(980, 620), padding=16, gap=12) as app:
    bs.Label("Employees", font="heading-lg")
    bs.Label(
        "Click a column header to sort · use the search box and column filters · "
        "select rows · add, edit, delete, group, and export from the toolbar.",
        font="body-sm",
    )

    selection = bs.Label("No rows selected", font="caption")

    table = bs.Table(
        columns=COLUMNS,
        rows=ROWS,
        selection_mode="multi",
        searchable=True,
        allow_filter=True,
        allow_group=True,
        allow_add=True,
        allow_edit=True,
        allow_delete=True,
        allow_export=True,
        striped=True,
        show_status_bar=True,
        page_size=10,
        fill="both",
        expand=True,
    )

    def show_selection(e):
        records = e.records
        if records:
            names = ", ".join(r["name"] for r in records[:3])
            extra = f" +{len(records) - 3} more" if len(records) > 3 else ""
            selection.text = f"{len(records)} selected: {names}{extra}"
        else:
            selection.text = "No rows selected"

    table.on_selection_changed(show_selection)

    def show_export(e):
        where = e.path if e.target == "file" else "the clipboard"
        selection.text = f"Exported {e.count} rows ({e.format}) to {where}"

    table.on_export(show_export)

app.run()
