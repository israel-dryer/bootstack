"""Visual test for public PasswordEntry and TextArea widgets."""
from bootstack.widgets.public import App, VStack, HStack, Label, PasswordEntry, TextArea, Button


def main():
    with App(title="PasswordEntry + TextArea — visual test", minsize=(480, 100), padding=24, gap=14) as app:

        # PasswordEntry variants
        Label("PasswordEntry — basic (with visibility toggle)")
        PasswordEntry(label="Password")

        Label("PasswordEntry — custom mask character")
        PasswordEntry("secret", label="API key", mask_char="*")

        Label("PasswordEntry — no visibility toggle")
        PasswordEntry(label="PIN", show_toggle=False)

        Label("PasswordEntry — required")
        PasswordEntry(label="Required password", required=True)

        Label("PasswordEntry — disabled")
        PasswordEntry("hidden", label="Disabled", disabled=True)

        # TextArea variants
        Label("TextArea — basic")
        ta = TextArea("Initial content here.", label="Notes", height=3)

        Label("TextArea — with placeholder")
        TextArea(label="Description", placeholder="Type something...", height=3)

        Label("TextArea — read-only")
        TextArea(
            "This text cannot be edited.",
            label="Read-only",
            read_only=True,
            height=2,
        )

        Label("TextArea — max length (50 chars)")
        TextArea(label="Limited", max_length=50, height=2)

        # Controls
        with HStack(gap=8):
            Button("Clear notes", on_click=lambda: ta.clear(), variant="outline")
            Button("Select all", on_click=lambda: ta.select_all(), variant="outline")

    app.run()


if __name__ == "__main__":
    main()
