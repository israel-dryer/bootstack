"""Events — listening to widget activity with handlers and subscriptions.

Every widget announces what it does as named events. Bind a handler with an
`on_*()` shorthand and the handler receives the event directly: data-carrying
events (like `change`) hand it a typed payload whose attributes you read
(`e.value`), while native events (like `click`) hand it a curated `Event`.
Cancel the binding when you no longer need it.
"""

import bootstack as bs

with bs.App(title="Events", padding=16, gap=8, minsize=(380, 1)) as app:
    bs.Label("Your name", font="caption")
    name = bs.TextField(placeholder="Type and press Enter…")

    echo = bs.Label("", font="heading-md")
    clicks = bs.Label("Clicks: 0", font="caption")

    # Direct handler — fires on commit (blur or Enter). The handler receives a
    # ChangeEvent; read the committed value straight off the payload.
    name.on_change(lambda e: setattr(echo, "text", f"Hello, {e.value}!"))

    # For a simple action, the `on_click=` constructor argument takes a
    # no-argument callback.
    count = {"n": 0}

    def bump() -> None:
        count["n"] += 1
        clicks.text = f"Clicks: {count['n']}"

    greet = bs.Button("Greet", accent="primary", on_click=bump)

    # The `on_click()` method instead returns a Subscription and hands the
    # handler the curated Event — keep the Subscription to cancel it later.
    sub = greet.on_click(lambda e: bump())

    # Cancelling a subscription detaches the handler.
    bs.Button("Stop extra counting", on_click=sub.cancel)

app.run()
