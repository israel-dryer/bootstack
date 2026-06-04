"""Signals — reactive values that keep widgets and application state in sync.

Type in the name field and watch three things react to the same signal at once:
a greeting label, a live character count, and the Submit button's enabled state.
"""

import bootstack as bs

with bs.App(title="Signals", padding=16, gap=8, minsize=(360, 1)) as app:
    name = bs.Signal("World")

    # Derived signals recompute automatically whenever `name` changes.
    greeting = name.map(lambda n: f"Hello, {n}!" if n.strip() else "Hello there!")
    char_count = name.map(lambda n: f"{len(n)} characters")

    bs.Label("Your name", font="caption")
    bs.TextField(textsignal=name)

    bs.Label(textsignal=greeting, font="heading-md")
    bs.Label(textsignal=char_count, font="caption")

    submit = bs.Button(
        "Submit",
        accent="primary",
        on_click=lambda: bs.alert(f"Submitted: {name()}"),
    )

    # React imperatively: disable Submit while the field is empty.
    name.subscribe(lambda value: setattr(submit, "disabled", not value.strip()),
                   immediate=True)

app.run()