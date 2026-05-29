"""Visual test for public Toast, Tooltip, and Card widgets."""
from bootstack.widgets import (
    App, VStack, HStack, Card, Label, Button, Separator,
    TextField, Badge, Toast, toast, Tooltip,
)


def main():
    with App(title="Toast + Tooltip + Card", minsize=(560, 480), padding=24, gap=16) as app:

        # --- Card ---
        Label("Card — default styling")
        with Card(fill="x"):
            Label("Inside a Card", font="body[bold]")
            Label("Cards group related content with a border and padding.")
            with HStack(gap=8):
                Button("Primary action", accent="primary")
                Button("Secondary", variant="outline")

        with Card(fill="x", accent="primary", show_border=False):
            Label("Card with accent='primary', no border", font="body[bold]")
            Label("Useful for highlighted content sections.")

        Separator(fill="x")

        # --- Tooltip ---
        Label("Tooltip — hover over the buttons")
        with HStack(gap=12):
            b1 = Button("Hover me")
            Tooltip(b1, "This button does something helpful.", delay=200)

            b2 = Button("Anchored tip", accent="primary", variant="outline")
            Tooltip(b2, "Anchored below the button.", anchor_point="s", window_point="n", delay=200)

            b3 = Button("Long tip", variant="ghost")
            Tooltip(b3, "This is a longer tooltip that will wrap when it exceeds the wrap_width.", wrap_width=180, delay=200)

        Separator(fill="x")

        # --- Toast ---
        Label("Toast — click to trigger notifications")
        with HStack(gap=8):
            Button(
                "Default toast",
                on_click=lambda: toast("File saved successfully.", duration=3000),
            )
            Button(
                "Success",
                accent="success",
                on_click=lambda: toast(
                    "Operation completed.",
                    title="Success",
                    accent="success",
                    icon="check-circle",
                    duration=3000,
                ),
            )
            Button(
                "Danger",
                accent="danger",
                on_click=lambda: toast(
                    "Something went wrong.",
                    title="Error",
                    accent="danger",
                    icon="exclamation-triangle",
                    duration=4000,
                ),
            )

        with HStack(gap=8):
            Button(
                "With actions",
                variant="outline",
                on_click=lambda: Toast(
                    title="Delete item?",
                    message="This action cannot be undone.",
                    accent="warning",
                    actions=[
                        {"text": "Cancel", "variant": "ghost"},
                        {"text": "Delete", "accent": "danger"},
                    ],
                    on_dismiss=lambda btn: print(f"Dismissed via: {btn}"),
                ).show(),
            )
            Button(
                "No auto-dismiss",
                variant="outline",
                on_click=lambda: Toast(
                    title="Persistent toast",
                    message="Close me manually.",
                    detail="no timeout",
                    duration=None,
                ).show(),
            )

    app.run()


if __name__ == "__main__":
    main()
