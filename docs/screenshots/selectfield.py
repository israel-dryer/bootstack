import bootstack as bs

COUNTRIES = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "Mexico", "Spain", "United Kingdom", "United States",
]


def hero():
    with bs.App(title="Select", size=(540, 300), padding=20) as app:
        sel = bs.Select(COUNTRIES, label="Country", value="France", fill="x")

    app.tk.after(850, sel._internal._show_selection_options)
    app.run()


def states():
    with bs.App(title="Select — States", padding=20) as app:
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            normal = bs.Select(["A", "B", "C"], value="A", label="Normal")
            bs.Select(["A", "B", "C"], value="A", label="Read only", read_only=True)
            bs.Select(["A", "B", "C"], value="A", label="Disabled",  disabled=True)

    app.tk.after(200, normal._internal._entry.focus_set)
    app.run()


SCENES = {
    "hero":   hero,
    "states": states,
}