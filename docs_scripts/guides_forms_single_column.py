import bootstack as bs

app = bs.App(title="Sign in", size=(360, 300))
form = bs.Card(app)
form.pack(fill="both", expand=True, padx=20, pady=20)

email = bs.TextEntry(form, label="Email", required=True)
email.add_validation_rule("email", message="Enter a valid email address.")
email.pack(fill="x")

password = bs.PasswordEntry(form, label="Password", required=True)
password.pack(fill="x", pady=(8, 12))

def submit():
    if email.validation(email.value, "manual") and password.value:
        print("signing in:", email.value)

bs.Button(form, text="Sign in", accent="primary", command=submit)\
    .pack(fill="x")

app.mainloop()