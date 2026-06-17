import bootstack as bs

COUNTRIES = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "Mexico", "Spain", "United Kingdom", "United States",
]


def hero():
    with bs.App(title="Select", size=(540, 300), padding=20) as app:
        sel = bs.Select(COUNTRIES, label="Country", value="France", horizontal="stretch")

    app.tk.after(850, sel._internal._show_selection_options)
    app.run()


def grouping():
    with bs.App(title="Select — Grouping", size=(540, 300), padding=20) as app:
        sel = bs.Select(
            options=[
                {"text": "Apple",    "value": "apple",    "category": "Fruit"},
                {"text": "Banana",   "value": "banana",   "category": "Fruit"},
                {"text": "Cherry",   "value": "cherry",   "category": "Fruit"},
                {"text": "Carrot",   "value": "carrot",   "category": "Vegetable"},
                {"text": "Broccoli", "value": "broccoli", "category": "Vegetable"},
                {"text": "Basil",    "value": "basil",    "category": "Herb"},
                {"text": "Mint",     "value": "mint",     "category": "Herb"},
            ],
            group_by="category",
            label="Ingredient",
            value="banana",
            horizontal="stretch",
        )

    app.tk.after(850, sel._internal._show_selection_options)
    app.run()


def states():
    with bs.App(title="Select — States", padding=20) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            normal = bs.Select(["A", "B", "C"], value="A", label="Normal")
            bs.Select(["A", "B", "C"], value="A", label="Read only", read_only=True)
            bs.Select(["A", "B", "C"], value="A", label="Disabled",  disabled=True)

    app.tk.after(200, normal._internal._entry.focus_set)
    app.run()


SCENES = {
    "hero":     hero,
    "grouping": grouping,
    "states":   states,
}