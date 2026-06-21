import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(600, 300), padding=0) as app:
        def open_confirm():
            def build(content):
                bs.Spacer()
                with bs.Row(gap=16, vertical_items="center", padding=(20, 0),
                            horizontal="stretch"):
                    bs.Label(icon={"name": "x-circle-fill", "size": 48}, accent="danger")
                    with bs.Column(gap=4, horizontal_items="left"):
                        bs.Label("Delete 13 items permanently?")
                        bs.Label("This action cannot be undone.",
                                 font="caption", accent="secondary")
                bs.Spacer()

            _dlg[0] = Dialog(
                title="Confirm Delete",
                content_builder=build,
                buttons=[
                    DialogButton("Cancel", role="cancel"),
                    DialogButton("Delete", role="danger", result="delete"),
                ],
                min_size=(420, 160),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_confirm)
        app.tk.after(850, lift_dialog)
    app.run()


def alert():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 280), padding=0) as app:
        def open_alert():
            def build(content):
                bs.Spacer()
                with bs.Row(gap=16, vertical_items="center", padding=(20, 0),
                            horizontal="stretch"):
                    bs.Label(icon={"name": "check-circle-fill", "size": 48}, accent="success")
                    bs.Label("File saved successfully.")
                bs.Spacer()

            _dlg[0] = Dialog(
                title="Done",
                content_builder=build,
                buttons=[DialogButton("OK", role="secondary", default=True)],
                min_size=(360, 140),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_alert)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero, "alert": alert}
