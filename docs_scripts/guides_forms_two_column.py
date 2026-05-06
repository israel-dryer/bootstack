import bootstack as bs

app = bs.App(title="Multi Column Form")

form = bs.Form(
    app,
    col_count=2,
    items=[
        {"key": "first",    "label": "First name", "editor": "textentry"},
        {"key": "last",     "label": "Last name",  "editor": "textentry"},
        {"key": "email",    "label": "Email",      "editor": "textentry",
         "columnspan": 2},
        {"key": "city",     "label": "City",       "editor": "textentry"},
        {"key": "zip",      "label": "ZIP",        "editor": "textentry"},
        {"key": "verified", "label": "Email verified",
         "editor": "checkbutton", "columnspan": 2},
    ],
    buttons=["Cancel", "Save"],
)
form.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()