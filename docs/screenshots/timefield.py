import datetime

import bootstack as bs

NOW = datetime.time(14, 30)


def hero():
    with bs.App(title="TimeField", padding=20, size=(360, 360)) as app:
        tf = bs.TimeField(
            value=NOW,
            label="Meeting time",
            message="Select the meeting start time.",
            fill="x",
        )
        app.tk.after(850, tf._internal._show_selection_options)
    app.run()


def formats():
    with bs.App(title="TimeField — Formats", padding=20, gap=12, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.TimeField(value=NOW, label="Short (default)", value_format="shortTime")
            bs.TimeField(value=NOW, label="24-hour",         value_format="HH:mm")
            bs.TimeField(value=NOW, label="24-hour long",    value_format="HH:mm:ss")
    app.run()


def intervals():
    with bs.App(title="TimeField — Intervals", padding=20, gap=12, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.TimeField(value=NOW, label="15-min intervals", interval=15)
            bs.TimeField(value=NOW, label="30-min intervals", interval=30)
            bs.TimeField(value=NOW, label="60-min intervals", interval=60)
    app.run()


def states():
    with bs.App(title="TimeField — States", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.TimeField(value=NOW, label="Normal")
            bs.TimeField(value=NOW, label="Read only", read_only=True)
            bs.TimeField(value=NOW, label="Disabled",  disabled=True)
    app.run()


SCENES = {
    "hero":      hero,
    "formats":   formats,
    "intervals": intervals,
    "states":    states,
}