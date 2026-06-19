from bootstack.dialogs._impl.colorchooser import ColorChooserDialog as _CCD
import bootstack as bs

_COLOR = "#186be7"      # the "Current" (initial) color
_NEW = "#dc3545"        # a contrasting "New" pick, so the two previews differ


def _open_scene(select_tab=None):
    """Open the color dialog non-modally and (optionally) switch tabs."""
    _dlg = [None]
    with bs.App(title=" ", size=(720, 620), padding=0) as app:
        def open_color():
            _dlg[0] = _CCD(initial_color=_COLOR)
            _dlg[0].show(modal=False)
            if _dlg[0]._chooser:
                if select_tab:
                    _dlg[0]._chooser.notebook.select(select_tab)
                # Pick a different color so "New" contrasts with "Current".
                _dlg[0]._chooser.on_press_swatch(_NEW)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0]._dialog and _dlg[0]._dialog.toplevel):
                return
            top = _dlg[0]._dialog.toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_color)
        app.tk.after(850, lift_dialog)
    app.run()


def hero():
    _open_scene(select_tab="themed")


def custom():
    _open_scene(select_tab="custom")


SCENES = {"hero": hero, "custom": custom}
