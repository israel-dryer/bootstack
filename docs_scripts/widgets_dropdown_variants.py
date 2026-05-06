import bootstack as bs

app = bs.App(title="Dropdown variants")
frm = bs.PackFrame(app, padding=16, gap=8, direction="horizontal").pack()

bs.DropdownButton(frm, text="Primary", accent="primary", items=[]).pack()
bs.DropdownButton(frm, text="Outline", accent="secondary", variant="outline", items=[]).pack()
bs.DropdownButton(frm, text="Ghost", accent="success", variant="ghost", items=[]).pack()

app.mainloop()
