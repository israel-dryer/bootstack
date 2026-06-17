"""Toasts, notifications, and snackbars — click each to compare."""
import bootstack as bs


with bs.App(title="Transient messages", size=(560, 360), padding=20, gap=12) as app:
    bs.Label("Transient messages", font="heading-lg")
    bs.Label("Three surfaces, each for a different job.", accent="secondary")

    with bs.GroupBox("toast() — passive, auto-dismiss", horizontal="stretch"):
        with bs.Row(gap=8):
            bs.Button("Saved", accent="success",
                      on_click=lambda: bs.toast("Your changes were saved.",
                                                icon="check-circle", accent="success"))
            bs.Button("Low battery", accent="warning",
                      on_click=lambda: bs.toast("Battery at 12%.",
                                                icon="battery-half", accent="warning"))

    with bs.GroupBox("Notification — persistent, closes on demand", horizontal="stretch"):
        bs.Button("Notify",
                  on_click=lambda: bs.Notification(
                      "Backup complete",
                      message="3.2 GB uploaded to the cloud.",
                      detail="just now", icon="cloud-check", accent="success",
                  ).show())

    with bs.GroupBox("Snackbar — one action, window bottom edge", horizontal="stretch"):
        with bs.Row(gap=8):
            bs.Button("Archive",
                      on_click=lambda: bs.snackbar("Conversation archived.",
                                                   action="Undo",
                                                   on_action=lambda: bs.toast("Restored.")))
            bs.Button("Copy",
                      on_click=lambda: bs.snackbar("Copied to clipboard."))

app.run()
