"""Scene screenshots for the Composing Fields how-to.

One scene per recipe, each a self-contained field with addons. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py composing-fields
"""
import datetime

import bootstack as bs


def search():
    with bs.App(title="Search field", minsize=(560, 1), padding=20) as app:
        field = bs.TextField(placeholder="Search products...", value="wireless", fill="x")
        field.insert_addon("label", "before", icon="search")

        def clear():
            field.value = ""

        field.insert_addon("button", "after", name="clear", icon="x-lg", on_click=clear)
    app.run()


def amount():
    with bs.App(title="Amount field", minsize=(560, 1), padding=20) as app:
        price = bs.NumberField(value=1499, label="Price", fill="x")
        price.insert_addon("label", "before", text="$")
        price.insert_addon("label", "after", text="USD", accent="secondary")
    app.run()


def birthday():
    with bs.App(title="Birthday picker", minsize=(560, 1), padding=20) as app:
        bday = bs.DateField(label="Date of birth", value=datetime.date(1990, 5, 4), fill="x")
        bday.insert_addon("label", "before", icon="cake")
    app.run()


def unit():
    with bs.App(title="Unit field", minsize=(560, 1), padding=20) as app:
        size = bs.NumberField(value=64, label="Width", fill="x")
        percent = bs.Signal(True)  # False -> px, True -> %
        size.insert_addon("toggle", "after", name="unit", text="%", signal=percent)
    app.run()


def copy():
    with bs.App(title="Copy field", minsize=(560, 1), padding=20) as app:
        key = bs.TextField(value="sk-live-7f3a9c2b", label="API key", read_only=True, fill="x")

        def do_copy():
            key.set_clipboard(key.value)

        key.insert_addon("button", "after", name="copy", icon="clipboard",
                         on_click=do_copy, active_when_readonly=True)
    app.run()


SCENES = {
    "search": search,
    "amount": amount,
    "birthday": birthday,
    "unit": unit,
    "copy": copy,
}
