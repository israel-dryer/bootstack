"""Input Dialogs screenshot hero — captures the ask_string dialog directly."""
import bootstack as bs
from bootstack.dialogs.query import QueryDialog as _QueryDialog

_dlg = None

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_input():
        global _dlg
        _dlg = _QueryDialog(
            prompt="Enter a name for the new contact:",
            title="New Contact",
            value="",
        )
        _dlg._dialog.show(modal=False)

    def lift_dialog():
        if not (_dlg and _dlg._dialog and _dlg._dialog.toplevel):
            return
        top = _dlg._dialog.toplevel
        top.attributes("-topmost", True)
        top.lift()
        app._capture_target = top

    app.tk.after(200, open_input)
    app.tk.after(850, lift_dialog)

app.run()
