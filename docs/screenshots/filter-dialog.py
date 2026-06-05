from bootstack.dialogs.filterdialog import FilterDialog as _FD
import bootstack as bs

ITEMS = ["Australia", "Canada", "France", "Germany", "India",
         "Japan", "Mexico", "Spain", "UK", "USA"]


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 580), padding=0) as app:
        def open_filter():
            _dlg[0] = _FD(
                title="Filter Countries",
                items=ITEMS,
                enable_search=True,
                enable_select_all=True,
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_filter)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero}