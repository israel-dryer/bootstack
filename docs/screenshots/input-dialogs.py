import bootstack as bs
from bootstack.dialogs._impl.query import QueryDialog as _QueryDialog
from bootstack.dialogs._impl.datedialog import DateDialog as _DateDialog
from datetime import date


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 280), padding=0) as app:
        def open_input():
            _dlg[0] = _QueryDialog(
                prompt="Enter a name for the new contact:",
                title="New Contact",
                value="",
            )
            _dlg[0]._dialog.show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_input)
        app.tk.after(850, lift_dialog)
    app.run()


def date_picker():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 480), padding=0) as app:
        def open_date():
            _dlg[0] = _DateDialog(
                title="Pick a Deadline",
                initial_date=date(2025, 6, 15),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_date)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero, "date": date_picker}