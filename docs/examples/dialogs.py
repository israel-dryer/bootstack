import bootstack as bs

from bootstack.dialogs import Dialog, DialogButton, FormDialog
def show_custom():
    def build(frame):
        with bs.VStack(padding=20, gap=8, parent=frame):
            bs.Label("Are you sure you want to delete 3 items?")
            bs.Label("This action cannot be undone.", font="caption")

    dlg = Dialog(
        title="Delete items",
        content_builder=build,
        buttons=[
            DialogButton("Delete", role="danger", result="delete", default=True),
            DialogButton("Cancel", role="cancel"),
        ],
    )
    dlg.show()

def show_form():
    dlg = FormDialog(
        title="New Contact",
        data={"name": "", "email": "", "phone": ""},
    )
    dlg.show()

with bs.App(title="Dialogs demo", size=(700, 400), padding=20, gap=16) as app:

    # ── Alerts and Confirmations ───────────────────────────────────────────
    bs.Label("Alerts and Confirmations", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Alert",   on_click=lambda: bs.alert("Operation completed.", title="Done", ok_text="Got it"))
        bs.Button("Confirm", on_click=lambda: bs.confirm("Overwrite file?"))
        bs.Button("Confirm (danger)", on_click=lambda: bs.confirm(
            "Delete 3 items permanently?",
            title="Confirm Delete",
            confirm_text="Delete",
            confirm_role="danger",
        ))

    bs.Separator(fill="x")

    # ── Input Dialogs ──────────────────────────────────────────────────────
    bs.Label("Input Dialogs", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Text",      on_click=lambda: bs.ask_string("Enter your name:", title="Name"))
        bs.Button("Integer",   on_click=lambda: bs.ask_integer("Enter age:", min_value=0, max_value=120))
        bs.Button("Float",     on_click=lambda: bs.ask_float("Enter price:", min_value=0.0, step=0.5))
        bs.Button("Date",      on_click=lambda: bs.ask_date(title="Select Date"))
        bs.Button("Date range", on_click=lambda: bs.ask_date_range(title="Select Range"))
        bs.Button("From list", on_click=lambda: bs.ask_item("Select country:", ["Canada", "UK", "USA", "Other"]))

    bs.Separator(fill="x")

    # ── Custom and Form Dialogs ────────────────────────────────────────────
    bs.Label("Custom and Form Dialogs", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("Custom dialog", on_click=show_custom)
        bs.Button("Form dialog",   on_click=show_form)

app.run()