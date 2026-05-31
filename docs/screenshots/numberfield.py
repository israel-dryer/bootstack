import bootstack as bs

with bs.App(title="NumberField", padding=20, gap=14) as app:

    basic = bs.NumberField(
        label="Quantity",
        message="Enter a value between 0 and 100.",
        fill="x",
    )

    bounded = bs.NumberField(
        50,
        label="Bounded (0–100, step 5)",
        min_value=0,
        max_value=100,
        step=5,
        fill="x",
    )

    with bs.Grid(columns=[1, 1], gap=8, fill="x", sticky_items="ew"):
        bs.NumberField(value=0.0, label="Float (step 0.1)", step=0.1)
        bs.NumberField(           label="No steppers",      show_steppers=False)
        bs.NumberField(value=1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
        bs.NumberField(value=9.99,    value_format="currency", label="Currency",   show_steppers=False)
        bs.NumberField(value=3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
        bs.NumberField(value=0.75,    value_format="percent",  label="Percent",    show_steppers=False)

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.NumberField(value=42, label="Normal")
        bs.NumberField(value=42, label="Read only", read_only=True)
        bs.NumberField(value=42, label="Disabled",  disabled=True)

    app.tk.after(150, bounded.focus)
    app.tk.after(450, basic.focus)

app.run()
