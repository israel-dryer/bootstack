import bootstack as bs

from bootstack.dialogs import Dialog, DialogButton
def show_simple():
    dlg = Dialog(
        title="Confirm deletion",
        content_builder=lambda frame: [
            bs.Column(padding=(24, 20), gap=8, parent=frame),
            bs.Label("Delete 3 selected items?"),
            bs.Label("This action cannot be undone.", font="caption"),
        ],
        buttons=[
            DialogButton("Delete", role="danger", result="delete"),
            DialogButton("Cancel", role="cancel"),
        ],
    )
    dlg.show()

def show_info():
    def build(frame):
        with bs.Column(padding=24, gap=12, parent=frame):
            bs.Label("New version available", font="heading-sm")
            bs.Label("bootstack 2.1.0 is ready to install.")
            bs.Label("Release notes: improved themes, new widgets.", font="caption")

    dlg = Dialog(
        title="Update available",
        content_builder=build,
        buttons=[
            DialogButton("Install now", role="primary", result="install", default=True),
            DialogButton("Later",       role="cancel"),
        ],
        min_size=(420, 180),
    )
    dlg.show()

def show_anchored():
    def build(frame):
        with bs.Column(padding=16, gap=8, parent=frame):
            bs.Label("Saved to Documents/report.pdf")

    dlg = Dialog(
        title=" ",
        content_builder=build,
        buttons=[DialogButton("OK", role="secondary", result=True, default=True)],
        min_size=(320, 100),
    )
    dlg.show()

with bs.App(title="Dialog", size=(680, 200), padding=20, gap=16) as app:

    bs.Label("Custom Dialog", font="heading-sm")
    with bs.Row(gap=8):
        bs.Button("Delete confirmation", on_click=show_simple)
        bs.Button("Update notice",       on_click=show_info)
        bs.Button("Simple message",      on_click=show_anchored)

app.run()