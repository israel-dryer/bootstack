from bootstack.dialogs.formdialog import FormDialog as _InternalFormDialog
import bootstack as bs


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 500), padding=0) as app:
        def open_form():
            _dlg[0] = _InternalFormDialog(
                None,
                title="New Contact",
                data={"name": "", "email": "", "phone": ""},
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_form)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero}