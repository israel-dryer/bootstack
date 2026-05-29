"""Visual test for public SizeGrip and Scrollbar widgets."""
from bootstack import (
    App, VStack, HStack, Label, TextArea, Separator, SizeGrip, Scrollbar,
)


def main():
    with App(title="SizeGrip + Scrollbar", minsize=(480, 400), padding=20, gap=16) as app:

        # Scrollbar — shown standalone (vertical and horizontal)
        Label("Scrollbar — standalone (unsized, fills parent)", font="body[bold]")
        with HStack(gap=12, fill="x"):
            with VStack(gap=4, fill="x", expand=True):
                Label("vertical")
                Scrollbar(orient="vertical", fill="y")
            with VStack(gap=4, fill="x", expand=True):
                Label("horizontal")
                Scrollbar(orient="horizontal", fill="x")
            with VStack(gap=4, fill="x", expand=True):
                Label("accent='primary'")
                Scrollbar(orient="vertical", accent="primary", fill="y")

        Separator(fill="x")

        # TextArea has a built-in scrollbar — demonstrates the real use case
        Label("TextArea (built-in scrollbar for reference)", font="body[bold]")
        TextArea(
            "\n".join(f"Line {i}: The quick brown fox jumps over the lazy dog." for i in range(1, 30)),
            height=120,
            fill="x",
        )

        Separator(fill="x")

        Label("SizeGrip — drag bottom-right corner to resize", font="body[bold]")
        with HStack(fill="x"):
            Label("Resize this window by dragging the handle in the bottom-right corner.")

    # SizeGrip placed at the bottom-right of the window via place()
    sg = SizeGrip()
    sg._internal.place(relx=1.0, rely=1.0, anchor="se")

    app.run()


if __name__ == "__main__":
    main()