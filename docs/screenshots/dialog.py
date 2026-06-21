import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 280), padding=0) as app:
        def open_dialog():
            def build(content):
                with bs.Column(gap=6, horizontal_items="left", horizontal="stretch"):
                    bs.Label("Publish report to the team?")
                    bs.Label("All 12 members will be notified.",
                             font="caption", accent="secondary")

            _dlg[0] = Dialog(
                title="Publish Report",
                content_builder=build,
                padding=(24, 20, 24, 8),
                buttons=[
                    DialogButton("Cancel", role="cancel"),
                    DialogButton("Publish", role="primary", result="publish", default=True),
                ],
                min_size=(360, 0),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_dialog)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero}
