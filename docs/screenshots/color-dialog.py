"""Color Dialog screenshot hero — captures the dialog window directly."""
from bootstack.dialogs.colorchooser import ColorChooserDialog as _CCD
import bootstack as bs

_dlg = None
_COLOR = "#186be7"

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_color():
        global _dlg
        _dlg = _CCD(initial_color=_COLOR)
        _dlg.show(modal=False)

    def lift_dialog():
        if not (_dlg and _dlg._dialog and _dlg._dialog.toplevel):
            return
        top = _dlg._dialog.toplevel
        top.attributes("-topmost", True)
        top.lift()
        # Point the runner at the dialog window for capture.
        app._capture_target = top
        if _dlg._chooser:
            try:
                _dlg._chooser.preview.configure(bg=_COLOR)
                _dlg._chooser.preview_lbl.configure(bg=_COLOR, fg="white")
            except Exception:
                pass

    app.tk.after(200, open_color)
    app.tk.after(850, lift_dialog)

app.run()