import bootstack as bs

app = bs.App(title="Card Form Demo", theme='light')

outer = bs.PackFrame(app, padding=32, direction='column', gap=0, fill_items='x').pack(fill='both', expand=True)

card = bs.Card(outer)
card.pack(fill='x')

form_frame = bs.PackFrame(card, direction='column', gap=12, fill_items='x', padding=4)
form_frame.pack(fill='x')

bs.Label(form_frame, text="Personal Information", font="heading-sm[bold]").pack(anchor='w')
bs.Separator(form_frame).pack(fill='x')

bs.TextEntry(form_frame, label="Full Name").pack()
bs.TextEntry(form_frame, label="Email Address").pack()
bs.PathEntry(form_frame, label="Project Folder").pack()
bs.SelectBox(form_frame, label="Department", items=["Engineering", "Science", "Operations", "Finance"]).pack()

btn_row = bs.PackFrame(form_frame, direction='row', gap=8)
btn_row.pack(anchor='e')
bs.Button(btn_row, text="Cancel").pack()
bs.Button(btn_row, text="Save", accent='primary').pack()

app.mainloop()
