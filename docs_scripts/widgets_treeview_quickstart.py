import bootstack as bs

app = bs.App(title="TreeView quickstart", size=(560, 420))

tree = bs.TreeView(app, columns=("size", "modified"))

tree.heading("#0",       text="Name",     anchor="w")
tree.heading("size",     text="Size",     anchor="e")
tree.heading("modified", text="Modified", anchor="w")

tree.column("#0",       width=260, anchor="w")
tree.column("size",     width=90,  anchor="e", stretch=False)
tree.column("modified", width=130, anchor="w", stretch=False)

documents = tree.insert("", "end", text="Documents", open=True, values=("",      "2026-05-10"))
tree.insert(documents, "end", text="Report.pdf",                 values=("1.2 MB", "2026-05-08"))
tree.insert(documents, "end", text="Notes.txt",                  values=("12 KB",  "2026-05-09"))

images = tree.insert(documents, "end", text="Images", open=True, values=("",       "2026-04-22"))
tree.insert(images, "end", text="photo-01.jpg",                  values=("3.4 MB", "2026-04-22"))
tree.insert(images, "end", text="photo-02.jpg",                  values=("2.8 MB", "2026-04-22"))

projects = tree.insert("", "end", text="Projects",               values=("",       "2026-05-01"))
tree.insert(projects, "end", text="bootstack",                   values=("",       "2026-05-11"))
tree.insert(projects, "end", text="experiments",                 values=("",       "2026-03-14"))

tree.pack(fill="both", expand=True, padx=12, pady=12)

app.mainloop()