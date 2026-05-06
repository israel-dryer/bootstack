import bootstack as bs

app = bs.App(title="Create account", minsize=(420, 360))
form = bs.Card(app, padding=20)
form.pack(fill="both", expand=True, padx=20, pady=20)

email = bs.TextEntry(form, label="Email", required=True)
email.add_validation_rule("email", message="Enter a valid email address.")
email.pack(fill="x", pady=4)

username = bs.TextEntry(form, label="Username", required=True)
username.add_validation_rule(
    "stringLength", min=3, max=20,
    message="Username must be 3–20 characters.",
)
username.add_validation_rule(
    "pattern", pattern=r"^[a-zA-Z0-9_]+$",
    message="Letters, numbers, and underscores only.",
)
username.pack(fill="x", pady=4)

password = bs.PasswordEntry(form, label="Password", required=True)
password.add_validation_rule(
    "stringLength", min=8,
    message="At least 8 characters.",
)
password.pack(fill="x", pady=4)

confirm = bs.PasswordEntry(form, label="Confirm password", required=True)
confirm.add_validation_rule(
    "custom",
    func=lambda v: v == password.value,
    message="Passwords must match.",
    trigger="always",
)
confirm.pack(fill="x", pady=4)
password.on_changed(lambda _: confirm.validation(confirm.value, "manual"))

fields = [email, username, password, confirm]

def submit():
    results = [f.validation(f.value, "manual") for f in fields]
    if all(results):
        print("creating account for", username.value)

bs.Button(form, text="Create account", accent="primary", command=submit)\
    .pack(fill="x", pady=(12, 0))

app.mainloop()