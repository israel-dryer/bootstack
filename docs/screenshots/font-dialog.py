from bootstack.dialogs.fontdialog import FontDialog as _FD
import bootstack as bs


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(1200, 900), padding=0) as app:
        def open_font():
            _dlg[0] = _FD(master=app.tk)
            _dlg[0].show(modal=False, anchor_to=app.tk)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(100, open_font)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero}