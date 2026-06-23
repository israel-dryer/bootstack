"""Select — full feature demo.

Demonstrates basic usage, label, searchable filtering, custom values,
states, reactive binding, and runtime option updates.

Run with:
    python docs/examples/select.py
"""

import bootstack as bs

COUNTRIES = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "Mexico", "Spain", "United Kingdom", "United States",
]

with bs.App(title="Select Demo", padding=20, gap=16) as app:

    # Basic
    bs.Label("Basic", font="heading-sm")
    bs.Select(["Red", "Green", "Blue"], horizontal="stretch")
    bs.Select(["Red", "Green", "Blue"], value="Green", horizontal="stretch")

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.Select(
        ["Option A", "Option B", "Option C"],
        label="Choose an option",
        message="Select the option that best applies.",
        horizontal="stretch",
    )

    # Required
    bs.Label("Required", font="heading-sm")
    bs.Select(["Red", "Green", "Blue"], label="Color", required=True, horizontal="stretch")

    # Searchable
    bs.Label("Searchable", font="heading-sm")
    bs.Select(COUNTRIES, label="Country", searchable=True, horizontal="stretch")

    # Custom values
    bs.Label("Custom Values", font="heading-sm")
    bs.Select(
        ["Red", "Green", "Blue"],
        label="Color (custom allowed)",
        allow_custom_values=True,
        horizontal="stretch",
    )

    # Grouping — cluster the popup under headers by an option field
    bs.Label("Grouping", font="heading-sm")
    bs.Select(
        options=[
            {"text": "Apple",    "value": "apple",    "category": "Fruit"},
            {"text": "Banana",   "value": "banana",   "category": "Fruit"},
            {"text": "Carrot",   "value": "carrot",   "category": "Vegetable"},
            {"text": "Broccoli", "value": "broccoli", "category": "Vegetable"},
            {"text": "Basil",    "value": "basil",    "category": "Herb"},
        ],
        group_by="category",
        label="Ingredient",
        horizontal="stretch",
    )

    # Capped popup height — long list scrolls after ~6 rows
    bs.Label("Limited Popup Height", font="heading-sm")
    bs.Select(COUNTRIES, label="Country (max 6 visible)", max_visible_items=6, horizontal="stretch")

    # States
    bs.Label("States", font="heading-sm")
    with bs.Row(gap=8, horizontal="stretch", grow_items=True):
        bs.Select(["A", "B", "C"], value="A", label="Normal")
        bs.Select(["A", "B", "C"], value="A", label="Read only",  read_only=True)
        bs.Select(["A", "B", "C"], value="A", label="Disabled",   disabled=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    with bs.Column(gap=6, horizontal="stretch", horizontal_items="stretch"):
        color = bs.Signal("Red")
        bs.Select(["Red", "Green", "Blue"], label="Color", signal=color)
        color_lbl = bs.Label("Selected: Red", accent="secondary", font="caption")
        def _update_color(v):
            color_lbl.text = f"Selected: {v}"

        color.subscribe(_update_color)

    # Runtime option updates
    bs.Label("Runtime Updates", font="heading-sm")
    with bs.Column(gap=6, horizontal="stretch", horizontal_items="stretch"):
        sel = bs.Select(["Alpha", "Beta", "Gamma"])
        with bs.Row(gap=8):
            def _set_abc():
                sel.options = ["A", "B", "C"]

            def _set_123():
                sel.options = ["1", "2", "3"]

            bs.Button("Set ABC", variant="outline", on_click=_set_abc)
            bs.Button("Set 1-2-3", variant="outline", on_click=_set_123)

app.run()
