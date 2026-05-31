import bootstack as bs
from bootstack.validation import ValidationRule

with bs.App(title="TextField", padding=20, gap=14) as app:

    basic = bs.TextField(
        label="Email address",
        placeholder="you@example.com",
        message="We'll never share your email.",
        fill="x",
    )

    required = bs.TextField(label="Username", required=True, fill="x")
    required.add_validation_rule(ValidationRule(
        "required",
        message="Username is required.",
        trigger="blur",
    ))

    with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
        bs.TextField(value="Editable",  label="Normal")
        bs.TextField(value="Read only", label="Read only", read_only=True)
        bs.TextField(value="Disabled",  label="Disabled", disabled=True)

    # Focus required field then blur onto basic — triggers required validation.
    app.tk.after(150, required.focus)
    app.tk.after(450, basic.focus)

app.run()
