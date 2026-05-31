import bootstack as bs

COUNTRIES = [
    "Canada", "France", "Germany", "Italy", "Japan",
    "Mexico", "Spain", "United Kingdom", "United States",
]

with bs.App(title="Select", padding=20, gap=14) as app:

    basic = bs.Select(
        ["Option A", "Option B", "Option C"],
        label="Choose an option",
        message="Select the option that best applies.",
        fill="x",
    )

    bs.Select(COUNTRIES, label="Country", value="France", fill="x")

    required = bs.Select(
        ["Red", "Green", "Blue"],
        label="Required",
        required=True,
        fill="x",
    )

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.Select(["A", "B", "C"], value="A", label="Normal")
        bs.Select(["A", "B", "C"], value="A", label="Read only",  read_only=True)
        bs.Select(["A", "B", "C"], value="A", label="Disabled",   disabled=True)

    # Focus required then blur to basic — triggers required validation.
    app.tk.after(150, lambda: required._internal._entry.focus_set())
    app.tk.after(450, lambda: basic._internal._entry.focus_set())
    app.tk.after(500, lambda: required._internal._entry.validate(required._internal._entry.value, trigger="blur"))

app.run()
