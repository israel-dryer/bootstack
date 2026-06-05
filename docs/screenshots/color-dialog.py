from bootstack.dialogs.colorchooser import ColorChooserDialog as _CCD
import bootstack as bs

_COLOR = "#186be7"


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(720, 620), padding=0) as app:
        def open_color():
            _dlg[0] = _CCD(initial_color=_COLOR)
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top
            if _dlg[0]._chooser:
                try:
                    _dlg[0]._chooser.preview.configure(bg=_COLOR)
                    _dlg[0]._chooser.preview_lbl.configure(bg=_COLOR, fg="white")
                except Exception:
                    pass

        app.tk.after(200, open_color)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero}