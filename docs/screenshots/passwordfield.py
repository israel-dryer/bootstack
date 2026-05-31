import bootstack as bs

with bs.App(title="PasswordField", padding=20, gap=14) as app:

    first = bs.PasswordField(
        label="Password",
        placeholder="Enter password…",
        message="Must be at least 8 characters.",
        fill="x",
    )

    required = bs.PasswordField(label="Required", required=True, fill="x")

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.PasswordField(label="With toggle")
        bs.PasswordField(label="No toggle", show_visibility_toggle=False)

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.PasswordField(value="secret123", label="Normal")
        bs.PasswordField(value="secret123", label="Read only", read_only=True)
        bs.PasswordField(value="secret123", label="Disabled", disabled=True)

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.PasswordField(value="secret", label="Default mask")
        bs.PasswordField(value="secret", label="Asterisk mask", mask="*")

    # Focus required field, then blur it onto first — triggers blur validation.
    app.tk.after(150, required.focus)
    app.tk.after(450, first.focus)

app.run()
