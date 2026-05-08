import bootstack as bs

app = bs.App()

search = bs.TextEntry(app, label="Find").pack(padx=16, pady=16)

case_sensitive = bs.Signal(True)

def toggle_case():
    print('Toggled:', case_sensitive.get())

search.insert_addon(
    bs.CheckToggle,
    position="after",
    text="Aa",
    name="case-btn",
    signal=case_sensitive,
    command=toggle_case,
)

app.mainloop()