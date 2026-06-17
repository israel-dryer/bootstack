import bootstack as bs


def hero():
    with bs.App(title="SpinnerField", padding=20, minsize=(720, 1)) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            sf = bs.SpinnerField(
                label="Priority",
                options=["Low", "Medium", "High", "Critical"],
                value="Medium",
                message="Sets the task priority level.",
            )
            bs.SpinnerField(
                label="Quantity",
                value=1,
                min_value=1,
                max_value=99,
            )
        app.tk.after(200, sf.focus)
    app.run()


def modes():
    with bs.App(title="SpinnerField — Modes", padding=20, minsize=(720, 1)) as app:
        with bs.Row(gap=12, horizontal="stretch", grow_items=True):
            bs.SpinnerField(
                label="Text mode",
                options=["Small", "Medium", "Large", "X-Large"],
                value="Medium",
            )
            bs.SpinnerField(
                label="Numeric mode",
                value=10,
                min_value=0,
                max_value=100,
                step=5,
            )
    app.run()


def states():
    with bs.App(title="SpinnerField — States", padding=20, minsize=(720, 1)) as app:
        with bs.Row(gap=8, horizontal="stretch", grow_items=True):
            bs.SpinnerField(value=5, min_value=1, max_value=10, label="Normal")
            bs.SpinnerField(value=5, min_value=1, max_value=10, label="Read only", read_only=True)
            bs.SpinnerField(value=5, min_value=1, max_value=10, label="Disabled",  disabled=True)
    app.run()


SCENES = {
    "hero":   hero,
    "modes":  modes,
    "states": states,
}