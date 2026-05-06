import bootstack as bs

app = bs.App(title="Create account", minsize=(440, 460))
card = bs.Card(app, padding=20)
card.pack(fill="both", expand=True, padx=20, pady=20)

bs.Label(card, text="Create your account", font="heading-md")\
    .pack(anchor="w", pady=(0, 12))

email = bs.TextEntry(card, label="Email", required=True)
email.add_validation_rule("email", message="Enter a valid email address.")
email.pack(fill="x", pady=4)

username = bs.TextEntry(card, label="Username", required=True)
username.add_validation_rule(
    "stringLength", min=3, max=20,
    message="Username must be 3–20 characters.",
)
username.add_validation_rule(
    "pattern", pattern=r"^[a-zA-Z0-9_]+$",
    message="Letters, numbers, and underscores only.",
)
username.pack(fill="x", pady=4)

password = bs.PasswordEntry(card, label="Password", required=True)
password.add_validation_rule(
    "stringLength", min=8, message="At least 8 characters.",
)
password.pack(fill="x", pady=4)

confirm = bs.PasswordEntry(card, label="Confirm password", required=True)
confirm.add_validation_rule(
    "custom",
    func=lambda v: v == password.value,
    message="Passwords must match.",
    trigger="always",
)
confirm.pack(fill="x", pady=4)
password.on_changed(lambda _: confirm.validation(confirm.value, "manual"))

terms = bs.CheckButton(card, text="I agree to the Terms of Service")
terms.pack(anchor="w", pady=(8, 12))

fields = [email, username, password, confirm]
submit = bs.Button(card, text="Create account", accent="primary",
                   state="disabled")
submit.pack(fill="x")

valid_state = {f: False for f in fields}

def refresh_submit():
    submit.configure(state="normal" if all(valid_state.values()) and terms.value else "disabled")

for f in fields:
    def make_handler(field):
        def handler(data):
            valid_state[field] = data["is_valid"]
            refresh_submit()
        return handler
    f.on_validated(make_handler(f))

terms.configure(command=refresh_submit)

def on_submit():
    if all(valid_state.values()):
        print("creating account for", username.value)

submit.configure(command=on_submit)
app.mainloop()