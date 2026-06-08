import bootstack as bs

from bootstack.widgets.dialogs import FormDialog
def show_simple():
    dlg = FormDialog(
        title="New Contact",
        data={"name": "", "email": "", "phone": ""},
    )
    dlg.show()

def show_multi_col():
    dlg = FormDialog(
        title="Shipping Address",
        data={"street": "", "city": "", "state": "", "zip": ""},
        col_count=2,
    )
    dlg.show()

with bs.App(title="Form Dialog", size=(680, 400), padding=20, gap=16) as app:

    with bs.HStack(gap=8):
        bs.Button("New Contact",      on_click=show_simple)
        bs.Button("Address (2 cols)", on_click=show_multi_col)

app.run()