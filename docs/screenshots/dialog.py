import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.frame import Frame as _Frame


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 280), padding=0) as app:
        def open_dialog():
            def build(frame):
                container = _Frame(frame, padding=(24, 20, 24, 8))
                container.pack(fill="both")
                _Label(container, text="Publish report to the team?").pack(anchor="w")
                _Label(container, text="All 12 members will be notified.",
                       font="caption").pack(anchor="w", pady=(6, 0))

            _dlg[0] = Dialog(
                title="Publish Report",
                content_builder=build,
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