"""Visual test for public Label and Badge widgets."""
from bootstack import App, VStack, HStack, Label, Badge, Button
from bootstack.signals import Signal


with App(title="Label + Badge — visual test", minsize=(480, 200), padding=24, gap=16) as app:

    counter = Signal(0)
    status = Signal("idle")
    counter_label_signal = Signal("0")

    def increment():
        counter.set(counter.get() + 1)
        counter_label_signal.set(str(counter.get()))

    def toggle_status():
        status.set("running" if status.get() == "idle" else "idle")

    # Plain text labels
    with VStack(gap=6):
        Label("Plain label — default style")
        Label("Colored label", color="#e63946")
        Label("Muted label", color="#6c757d")
        Label(
            "Wrapped label — lorem ipsum dolor sit amet consectetur adipiscing elit",
            wrap_width=300,
        )

    # Reactive label
    with HStack(gap=8, anchor_items="center"):
        Label("Counter:")
        Label(text_signal=counter_label_signal)
        Button("Increment", on_click=increment, accent="primary", variant="outline")

    # Status toggle
    with HStack(gap=8, anchor_items="center"):
        Label("Status:")
        Label(text_signal=status)
        Button("Toggle", on_click=toggle_status, variant="outline")

    # Badges — square
    Label("Badges — square (default)")
    with HStack(gap=6):
        for accent in ("primary", "success", "warning", "danger"):
            Badge(accent, accent=accent)

    # Badges — pill
    Label("Badges — pill variant")
    with HStack(gap=6):
        for accent in ("primary", "success", "warning", "danger"):
            Badge(accent, accent=accent, variant="pill")

    # Count indicator
    with HStack(gap=8, anchor_items="center"):
        Label("Messages")
        Badge("99+", accent="danger", variant="pill")

app.run()
