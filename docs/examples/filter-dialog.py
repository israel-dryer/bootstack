import bootstack as bs

COUNTRIES = ["Australia", "Canada", "France", "Germany", "India",
             "Japan", "Mexico", "Spain", "UK", "USA"]

STATUS_ITEMS = [
    {"text": "Active",   "value": "active",   "selected": True},
    {"text": "Inactive", "value": "inactive", "selected": False},
    {"text": "Pending",  "value": "pending",  "selected": True},
    {"text": "Archived", "value": "archived", "selected": False},
]

def show_basic():
    result = bs.ask_filter(COUNTRIES, title="Filter Countries")
    if result is not None:
        print(f"Selected: {result}")

def show_with_search():
    result = bs.ask_filter(
        COUNTRIES,
        title="Filter Countries",
        enable_search=True,
        enable_select_all=True,
    )
    if result is not None:
        print(f"Selected: {result}")

def show_dict_items():
    dlg = bs.FilterDialog(
        title="Filter by Status",
        items=STATUS_ITEMS,
        enable_select_all=True,
    )
    dlg.show()
    if dlg.result is not None:
        print(f"Selected: {dlg.result}")

with bs.App(title="Filter Dialog", size=(680, 160), padding=20, gap=16) as app:

    bs.Label("Filter Dialog", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Basic",            on_click=show_basic)
        bs.Button("Search and select all", on_click=show_with_search)
        bs.Button("Dict items",       on_click=show_dict_items)

app.run()