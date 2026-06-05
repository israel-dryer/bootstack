"""Events — listening to widget activity with handlers and subscriptions.

Every widget announces what it does as named events. Bind a handler with an
``on_*()`` shorthand, read the payload from ``event.data``, and cancel the
binding when you no longer need it.
"""

import bootstack as bs

with bs.App(title="Events", padding=16, gap=8, minsize=(380, 1)) as app:
    bs.Label("Your name", font="caption")
    name = bs.TextField(placeholder="Type and press Enter…")

    echo = bs.Label("", font="heading-md")
    clicks = bs.Label("Clicks: 0", font="caption")

    # Direct handler — fires on commit (blur or Enter). The payload lives on
    # `event.data`; a field's change event carries the committed `value`.
    name.on_change(lambda e: setattr(echo, "text", f"Hello, {e.data['value']}!"))

    # A button's click handler takes no arguments. `on_click` returns a
    # Subscription — keep it so the binding can be cancelled later.
    count = {"n": 0}

    def bump() -> None:
        count["n"] += 1
        clicks.text = f"Clicks: {count['n']}"

    greet = bs.Button("Greet", accent="primary")
    sub = greet.on_click(bump)

    # Cancelling a subscription detaches the handler — the button goes quiet.
    bs.Button("Stop counting", on_click=sub.cancel)

app.run()