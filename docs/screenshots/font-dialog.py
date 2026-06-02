"""Font Dialog screenshot hero — captures the font selector directly."""
from bootstack.dialogs.fontdialog import FontDialog as _FD
import bootstack as bs

_dlg = None

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_font():
        global _dlg
        _dlg = _FD()
        _dlg.show(position=(200, 100), modal=False)

    def lift_dialog():
        if not (_dlg and _dlg._dialog and _dlg._dialog.toplevel):
            return
        top = _dlg._dialog.toplevel
        top.attributes("-topmost", True)
        top.lift()
        app._capture_target = top

    app.tk.after(200, open_font)
    app.tk.after(850, lift_dialog)

app.run()
