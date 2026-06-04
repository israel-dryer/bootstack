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
    bs.Select(["Red", "Green", "Blue"], fill="x")
    bs.Select(["Red", "Green", "Blue"], value="Green", fill="x")

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.Select(
        ["Option A", "Option B", "Option C"],
        label="Choose an option",
        message="Select the option that best applies.",
        fill="x",
    )

    # Required
    bs.Label("Required", font="heading-sm")
    bs.Select(["Red", "Green", "Blue"], label="Color", required=True, fill="x")

    # Searchable
    bs.Label("Searchable", font="heading-sm")
    bs.Select(COUNTRIES, label="Country", searchable=True, fill="x")

    # Custom values
    bs.Label("Custom Values", font="heading-sm")
    bs.Select(
        ["Red", "Green", "Blue"],
        label="Color (custom allowed)",
        allow_custom_values=True,
        fill="x",
    )

    # States
    bs.Label("States", font="heading-sm")
    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.Select(["A", "B", "C"], value="A", label="Normal")
        bs.Select(["A", "B", "C"], value="A", label="Read only",  read_only=True)
        bs.Select(["A", "B", "C"], value="A", label="Disabled",   disabled=True)

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    with bs.VStack(gap=6, fill="x"):
        color = bs.Signal("Red")
        bs.Select(["Red", "Green", "Blue"], label="Color", signal=color, fill="x")
        color_lbl = bs.Label("Selected: Red", accent="secondary", font="caption")
        color.subscribe(lambda v: setattr(color_lbl, 'text', f"Selected: {v}"))

    # Runtime option updates
    bs.Label("Runtime Updates", font="heading-sm")
    with bs.VStack(gap=6, fill="x"):
        sel = bs.Select(["Alpha", "Beta", "Gamma"], fill="x")
        with bs.HStack(gap=8):
            bs.Button("Set ABC", variant="outline",
                on_click=lambda: setattr(sel, 'options', ["A", "B", "C"]))
            bs.Button("Set 1-2-3", variant="outline",
                on_click=lambda: setattr(sel, 'options', ["1", "2", "3"]))

app.run()
