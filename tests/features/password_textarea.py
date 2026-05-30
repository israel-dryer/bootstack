"""Visual test for public PasswordField and TextArea widgets."""
from bootstack import App, VStack, HStack, Label, PasswordField, TextArea, Button


with App(title="PasswordField + TextArea — visual test", minsize=(480, 100), padding=24, gap=14) as app:

    # PasswordField variants
    Label("PasswordField — basic (with visibility toggle)")
    PasswordField(label="Password")

    Label("PasswordField — custom mask character")
    PasswordField("secret", label="API key", mask_char="*")

    Label("PasswordField — no visibility toggle")
    PasswordField(label="PIN", show_visibility_toggle=False)

    Label("PasswordField — required")
    PasswordField(label="Required password", required=True)

    Label("PasswordField — disabled")
    PasswordField("hidden", label="Disabled", disabled=True)

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
