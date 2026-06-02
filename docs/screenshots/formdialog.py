"""FormDialog screenshot hero — captures the form dialog directly."""
from bootstack.dialogs.formdialog import FormDialog as _InternalFormDialog
import bootstack as bs

_dlg = None

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_form():
        global _dlg
        _dlg = _InternalFormDialog(
            None,
            title="New Contact",
            data={"name": "", "email": "", "phone": ""},
        )
        _dlg.show(modal=False)

    def lift_dialog():
        if not (_dlg and _dlg.toplevel):
            return
        top = _dlg.toplevel
        top.attributes("-topmost", True)
        top.lift()
        app._capture_target = top

    app.tk.after(200, open_form)
    app.tk.after(850, lift_dialog)

app.run()
