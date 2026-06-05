import bootstack as bs

with bs.App(title="Message Dialogs", size=(680, 300), padding=20, gap=16) as app:

    # ── Alert ──────────────────────────────────────────────────────────────
    bs.Label("Alert", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Alert (info)",    on_click=lambda: bs.alert("File saved.", severity="info"))
        bs.Button("Alert (success)", on_click=lambda: bs.alert("Upload complete.", severity="success"))
        bs.Button("Alert (warning)", on_click=lambda: bs.alert("Disk space low.", severity="warning"))
        bs.Button("Alert (danger)",  on_click=lambda: bs.alert("Connection lost.", severity="danger"))

    bs.Separator(fill="x")

    # ── Confirm ────────────────────────────────────────────────────────────
    bs.Label("Confirm", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Confirm",           on_click=lambda: bs.confirm("Overwrite the existing file?"))
        bs.Button("Confirm (danger)",  on_click=lambda: bs.confirm(
            "Delete 3 items permanently?",
            title="Confirm Delete",
            confirm_text="Delete",
            severity="danger"
        ))
        bs.Button("Confirm (warning)", on_click=lambda: bs.confirm(
            "This will close all open tabs.",
            severity="warning",
        ))

app.run()