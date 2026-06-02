"""Feature demo for the dialogs public API.

Run with:  python tests/features/dialogs_features.py
"""
import bootstack as bs
from datetime import date


def show(result):
    bs.Toast(title="Result", detail=str(result), duration=3000).show()


with bs.App(title="Dialog Features", padding=20, gap=16) as app:


    # ── alert() ───────────────────────────────────────────────────────────────
    bs.Label("alert()", font="heading-sm")
    with bs.HStack(gap=8, fill="x"):
        bs.Button("Default",
            on_click=lambda: bs.alert("Operation completed."))
        bs.Button("ok_text",
            on_click=lambda: bs.alert("Your session has expired.", ok_text="Sign in again"))
        bs.Button("info",
            on_click=lambda: bs.alert("10 records imported.", title="Import complete", severity="info"))
        bs.Button("success",
            on_click=lambda: bs.alert("Changes saved.", title="Saved", severity="success"))
        bs.Button("warning",
            on_click=lambda: bs.alert("Disk space is low.", title="Warning", severity="warning"))
        bs.Button("danger",
            on_click=lambda: bs.alert("Connection failed.", title="Error", severity="danger"))
        bs.Button("icon override",
            on_click=lambda: bs.alert("Copied to clipboard.", icon="clipboard-check"))

    bs.Separator(fill="x")

    # ── confirm() ─────────────────────────────────────────────────────────────
    bs.Label("confirm()", font="heading-sm")
    with bs.HStack(gap=8, fill="x"):
        bs.Button("Default",
            on_click=lambda: show(bs.confirm("Continue?")))
        bs.Button("Custom text",
            on_click=lambda: show(bs.confirm(
                "Save before closing?",
                confirm_text="Save",
                cancel_text="Don't save",
            )))
        bs.Button("danger role",
            on_click=lambda: show(bs.confirm(
                "Delete 3 items permanently?",
                title="Confirm Delete",
                confirm_text="Delete",
                confirm_role="danger",
                severity="danger",
            )))
        bs.Button("warning severity",
            on_click=lambda: show(bs.confirm(
                "This will overwrite 12 files.",
                confirm_text="Overwrite",
                severity="warning",
            )))

    bs.Separator(fill="x")

    # ── ask_string / ask_integer / ask_float / ask_item ───────────────────────
    bs.Label("Input dialogs", font="heading-sm")
    with bs.HStack(gap=8, fill="x"):
        bs.Button("ask_string",
            on_click=lambda: show(bs.ask_string("Enter your name:")))
        bs.Button("ask_integer",
            on_click=lambda: show(bs.ask_integer("Enter age:", min_value=0, max_value=120)))
        bs.Button("ask_float",
            on_click=lambda: show(bs.ask_float("Enter price:", min_value=0.0, step=0.5)))
        bs.Button("ask_item",
            on_click=lambda: show(bs.ask_item(
                "Select country:", ["Canada", "UK", "USA", "Other"])))

    bs.Separator(fill="x")

    # ── ask_date / ask_date_range ─────────────────────────────────────────────
    bs.Label("Date dialogs", font="heading-sm")
    with bs.HStack(gap=8, fill="x"):
        bs.Button("ask_date",
            on_click=lambda: show(bs.ask_date(title="Pick a date")))
        bs.Button("ask_date (constrained)",
            on_click=lambda: show(bs.ask_date(
                title="Pick a future date",
                min_date=date.today(),
            )))
        bs.Button("ask_date_range",
            on_click=lambda: show(bs.ask_date_range(title="Select range")))

    bs.Separator(fill="x")

    # ── custom Dialog ─────────────────────────────────────────────────────────
    bs.Label("Custom dialog", font="heading-sm")

    def open_custom():
        from bootstack.widgets._impl.primitives.label import Label as _Label
        from bootstack.widgets._impl.primitives.frame import Frame as _Frame

        def build(frame):
            c = _Frame(frame, padding=(20, 16, 20, 8))
            c.pack(fill="both")
            _Label(c, text="Send report to all 48 team members?").pack(anchor="w")
            _Label(c, text="This cannot be undone.", font="caption").pack(anchor="w", pady=(4, 0))

        dlg = bs.Dialog(
            title="Confirm Send",
            content_builder=build,
            buttons=[
                bs.DialogButton("Cancel", role="cancel"),
                bs.DialogButton("Send", role="primary", result="send", default=True),
            ],
            min_size=(320, 0),
        )
        dlg.show()
        show(dlg.result)

    with bs.HStack(gap=8, fill="x"):
        bs.Button("Custom dialog", on_click=open_custom)

    bs.Separator(fill="x")

    # ── FormDialog ────────────────────────────────────────────────────────────
    bs.Label("FormDialog", font="heading-sm")

    def open_form():
        dlg = bs.FormDialog(
            title="New Contact",
            data={"name": "", "email": "", "phone": ""},
        )
        dlg.show()
        show(dlg.result)

    def open_form_2col():
        dlg = bs.FormDialog(
            title="Address",
            data={"street": "", "city": "", "state": "", "zip": ""},
            col_count=2,
        )
        dlg.show()
        show(dlg.result)

    with bs.HStack(gap=8, fill="x"):
        bs.Button("1 column", on_click=open_form)
        bs.Button("2 columns", on_click=open_form_2col)

app.run()