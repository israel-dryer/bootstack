"""Filter Dialog screenshot hero — captures the filter dialog directly."""
from bootstack.dialogs.filterdialog import FilterDialog as _FD
import bootstack as bs

ITEMS = ["Australia", "Canada", "France", "Germany", "India",
         "Japan", "Mexico", "Spain", "UK", "USA"]

_dlg = None

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_filter():
        global _dlg
        _dlg = _FD(
            title="Filter Countries",
            items=ITEMS,
            enable_search=True,
            enable_select_all=True,
        )
        _dlg.show(modal=False)

    def lift_dialog():
        if not (_dlg and _dlg._dialog and _dlg._dialog.toplevel):
            return
        top = _dlg._dialog.toplevel
        top.attributes("-topmost", True)
        top.lift()
        app._capture_target = top

    app.tk.after(200, open_filter)
    app.tk.after(850, lift_dialog)

app.run()
