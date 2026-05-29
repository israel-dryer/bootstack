"""Visual test for public dialog functions and FormDialog."""
from bootstack.widgets import (
    App, VStack, HStack, Label, Button, Separator,
    alert, confirm, ask_string, ask_integer, ask_float, ask_date, ask_item,
    FormDialog,
)


def main():
    with App(title="Public Dialogs", minsize=(540, 560), padding=20, gap=14) as app:

        result_lbl = Label("(click a button to see its result)")

        def show(v):
            result_lbl.value = f"result: {v!r}"

        # --- Module-level functions ---
        Label("Module-level functions", font="heading-lg")

        with HStack(gap=8, fill="x"):
            Button("alert()", on_click=lambda: (
                alert("This is an alert message.", title="Alert"),
                show(None),
            ))
            Button("confirm()", on_click=lambda: show(
                confirm("Do you want to proceed?", title="Confirm")
            ))

        with HStack(gap=8, fill="x"):
            Button("ask_string()", on_click=lambda: show(
                ask_string("Enter your name:", title="Ask String", value="Ada")
            ))
            Button("ask_integer()", on_click=lambda: show(
                ask_integer("Enter an age:", title="Ask Integer",
                            value=25, min_value=0, max_value=120)
            ))
            Button("ask_float()", on_click=lambda: show(
                ask_float("Enter a ratio:", title="Ask Float",
                          value=1.5, min_value=0.0, max_value=10.0, step=0.1)
            ))

        with HStack(gap=8, fill="x"):
            Button("ask_date()", on_click=lambda: show(
                ask_date("Select a date", title="Ask Date")
            ))
            Button("ask_item()", on_click=lambda: show(
                ask_item("Choose a language:", ["Python", "Rust", "Go", "TypeScript"],
                         title="Ask Item", value="Python")
            ))

        Separator(fill="x")

        # --- FormDialog ---
        Label("FormDialog", font="heading-lg")

        form_result_lbl = Label("(no result yet)")

        def _show_form():
            dlg = FormDialog(
                title="User Profile",
                data={
                    "name": "Ada Lovelace",
                    "email": "",
                    "age": 28,
                    "active": True,
                },
                col_count=1,
            )
            dlg.show()
            if dlg.result:
                form_result_lbl.value = f"result: {dlg.result}"
            else:
                form_result_lbl.value = "cancelled"

        Button("Open FormDialog", on_click=_show_form)

    app.run()


if __name__ == "__main__":
    main()