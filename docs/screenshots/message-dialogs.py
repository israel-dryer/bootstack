import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack._core.images import Image as _ImageService
from bootstack.style.style import get_theme_color as _get_theme_color


def hero():
    _dlg = [None]
    with bs.App(title=" ", size=(600, 300), padding=0) as app:
        def open_confirm():
            def build(frame):
                _Frame(frame).pack(fill="x", expand=True)
                container = _Frame(frame, padding=(20, 0))
                container.pack(fill="x")
                _Frame(frame).pack(fill="x", expand=True)
                try:
                    color = _get_theme_color("danger")
                    img = _ImageService.get_icon("x-circle-fill", 48, color)
                    icon_lbl = _Label(container, image=img)
                    icon_lbl.image = img
                    icon_lbl.pack(side="left", anchor="center", padx=(0, 16))
                except Exception:
                    pass
                msg_frame = _Frame(container)
                msg_frame.pack(side="left", anchor="center")
                _Label(msg_frame, text="Delete 13 items permanently?").pack(anchor="w")
                _Label(msg_frame, text="This action cannot be undone.",
                       font="caption").pack(anchor="w", pady=(4, 0))

            _dlg[0] = Dialog(
                title="Confirm Delete",
                content_builder=build,
                buttons=[
                    DialogButton("Cancel", role="cancel"),
                    DialogButton("Delete", role="danger", result="delete"),
                ],
                min_size=(420, 160),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_confirm)
        app.tk.after(850, lift_dialog)
    app.run()


def alert():
    _dlg = [None]
    with bs.App(title=" ", size=(560, 280), padding=0) as app:
        def open_alert():
            def build(frame):
                _Frame(frame).pack(fill="x", expand=True)
                container = _Frame(frame, padding=(20, 0))
                container.pack(fill="x")
                _Frame(frame).pack(fill="x", expand=True)
                try:
                    color = _get_theme_color("success")
                    img = _ImageService.get_icon("check-circle-fill", 48, color)
                    icon_lbl = _Label(container, image=img)
                    icon_lbl.image = img
                    icon_lbl.pack(side="left", anchor="center", padx=(0, 16))
                except Exception:
                    pass
                msg_frame = _Frame(container)
                msg_frame.pack(side="left", anchor="center")
                _Label(msg_frame, text="File saved successfully.").pack(anchor="w")

            _dlg[0] = Dialog(
                title="Done",
                content_builder=build,
                buttons=[DialogButton("OK", role="secondary", default=True)],
                min_size=(360, 140),
            )
            _dlg[0].show(modal=False)

        def lift_dialog():
            if not (_dlg[0] and _dlg[0].toplevel):
                return
            top = _dlg[0].toplevel
            top.attributes("-topmost", True)
            top.lift()
            app._capture_target = top

        app.tk.after(200, open_alert)
        app.tk.after(850, lift_dialog)
    app.run()


SCENES = {"hero": hero, "alert": alert}