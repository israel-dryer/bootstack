"""Message Dialogs screenshot hero — captures the confirm dialog directly."""
import bootstack as bs
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.frame import Frame as _Frame
from bootstack._core.images import Image as _ImageService
from bootstack.style.style import get_theme_color as _get_theme_color

_dlg = None

with bs.App(title=" ", size=(1, 1), padding=0) as app:

    def open_confirm():
        global _dlg

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

        _dlg = bs.Dialog(
            title="Confirm Delete",
            content_builder=build,
            buttons=[
                bs.DialogButton("Cancel", role="cancel"),
                bs.DialogButton("Delete", role="danger", result="delete"),
            ],
            min_size=(420, 160),
        )
        _dlg.show(modal=False)

    def lift_dialog():
        if not (_dlg and _dlg.toplevel):
            return
        top = _dlg.toplevel
        top.attributes("-topmost", True)
        top.lift()
        app._capture_target = top

    app.tk.after(200, open_confirm)
    app.tk.after(850, lift_dialog)

app.run()
