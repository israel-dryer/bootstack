import bootstack as bs
from bootstack.widgets.dialogs import Dialog, DialogButton
from bootstack.widgets._impl.primitives.label import Label as _Label
from bootstack.widgets._impl.primitives.frame import Frame as _Frame

_dlg = None

with bs.App(title="My App", size=(680, 340), padding=24) as app:

    with bs.VStack(fill="both", expand=True, gap=8):
        bs.Label("Document Editor", font="heading-lg")
        bs.Label("report-q2-2026.docx")
        bs.Separator(fill="x")
        bs.Label("Last saved: 2 minutes ago", font="caption")

    def open_dialog():
        global _dlg

        def build(frame):
            container = _Frame(frame, padding=(24, 20, 24, 8))
            container.pack(fill="both")
            _Label(container, text="Publish report to the team?").pack(anchor="w")
            _Label(container, text="All 12 members will be notified.",
                   font="caption").pack(anchor="w", pady=(6, 0))

        _dlg = Dialog(
            title="Publish Report",
            content_builder=build,
            buttons=[
                DialogButton("Cancel", role="cancel"),
                DialogButton("Publish", role="primary", result="publish", default=True),
            ],
            min_size=(360, 0),
        )
        _dlg.show(modal=False)

    def lift_dialog():
        if _dlg and _dlg.toplevel:
            _dlg.toplevel.attributes("-topmost", True)
            _dlg.toplevel.lift()

    app.tk.after(200, open_dialog)
    app.tk.after(850, lift_dialog)

app.run()