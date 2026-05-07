import bootstack as bs

app = bs.App(size=(200, 200))

menu = bs.ContextMenu(app)
menu.add_command(text="Open", icon="folder2-open", command=lambda: print("Open"))
menu.add_command(text="Rename", command=lambda: print("Rename"))
menu.add_separator()
menu.add_command(text="Delete", icon="trash", command=lambda: print("Delete"))

app.mainloop()