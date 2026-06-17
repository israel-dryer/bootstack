"""Hero screenshot for the Building Forms how-to.

A two-column form with a validation error surfaced on the email field. The
scene calls form.validate() so the rule runs and its message renders inline.
Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py building-forms
"""
import bootstack as bs


def form_validation():
    with bs.App(title="New account", size=(620, 400), padding=20) as app:
        form = bs.Form(
            col_count=2,
            data={
                "first": "Ada",
                "last": "Lovelace",
                "email": "ada@",
                "role": "Engineer",
            },
            items=[
                bs.FieldItem(key="first", label="First name"),
                bs.FieldItem(key="last", label="Last name"),
                bs.FieldItem(key="email", label="Email", columnspan=2,
                             editor_options={"show_message": True}),
                bs.FieldItem(key="role", label="Role", editor="select",
                             editor_options={"values": ["Engineer", "Designer", "Manager"]},
                             columnspan=2),
            ],
            buttons=["Cancel", {"text": "Create account", "role": "primary"}],
            grow=True, horizontal="stretch",
        )
        form.field("email").add_validation_rule("email", message="Enter a valid email address.")
        form.validate()
    app.run()


SCENES = {
    "validation": form_validation,
}
