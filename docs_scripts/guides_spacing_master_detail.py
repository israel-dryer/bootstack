import bootstack as bs

app = bs.App(title="Master/detail", minsize=(720, 420))

shell = bs.GridFrame(app, columns=["220px", 1], rows=[1],
                     sticky_items="nsew")
shell.pack(fill="both", expand=True)

# Sidebar: stacked buttons, all the same width.
sidebar = bs.PackFrame(shell, direction="vertical", gap=2, padding=12,
                       fill_items="x")
sidebar.grid()

bs.Label(sidebar, text="Folders", font="label").pack(anchor="w", pady=(0, 8))
bs.Button(sidebar, text="Inbox", variant="ghost").pack()
bs.Button(sidebar, text="Sent", variant="ghost").pack()
bs.Button(sidebar, text="Archive", variant="ghost").pack()

# Detail: a card that fills the rest of the window.
detail = bs.PackFrame(shell, direction="vertical", gap=12, padding=16)
detail.grid()

bs.Label(detail, text="Inbox", font="heading-md").pack(anchor="w")
bs.Label(detail, text="No new messages.").pack(anchor="w")

app.mainloop()