"""Hot-reload demo (plain App).

Run it live:   bootstack dev development/hot_reload_demo.py

Then edit anything inside the `with bs.App()` block below and save — the running
window updates in place. The counter Signal lives at module level (above the
block), so its value survives every reload.
"""
import bootstack as bs

clicks = bs.Signal(0)  # module-level -> survives reloads

with bs.App(title="Hot Reload Demo", padding=24, gap=12) as app:
    with app.add_toolbar() as tb:
        tb.add_button("File")
        tb.add_spacer()
        tb.add_theme_toggle()

    bs.Label("Edit me and save — I reload in place.", font="heading-md")
    bs.Label("Try changing this text, colors, or adding widgets.")

    count_label = bs.Label(textsignal=clicks.map(lambda n: f"Clicks: {n}"))
    bs.Button("Click me", accent="primary", on_click=lambda: clicks.set(clicks() + 1))

app.run()
