"""Toast screenshot hero."""
import bootstack as bs

with bs.App(title="Toast", size=(560, 280), padding=24, gap=8) as app:
    bs.Label("Toast Notifications", font="heading-md[bold]")
    bs.Label("Transient messages that auto-dismiss after a configurable delay.",
             font="caption")

    def show_toast():
        # Bottom-right corner of the captured window region.
        # App client area: ~(200, 131) to (760, 411) at runner position +200+100.
        # Toast ~400×80 px → right-aligned with 12px margin from edges.
        bs.Toast(
            title="File saved",
            message="report-2024.pdf was saved to your documents.",
            accent="success",
            icon="check-circle",
            duration=8000,
            position="+348+290",
        ).show()

    app.tk.after(850, show_toast)

app.run()
