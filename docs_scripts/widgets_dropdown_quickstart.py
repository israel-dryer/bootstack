import bootstack as bs

app = bs.App()

items = [
    bs.ContextMenuItem("command", text="Open", command=lambda: print("Open")),
    bs.ContextMenuItem("command", text="Rename", command=lambda: print("Rename")),
    bs.ContextMenuItem("separator"),
    bs.ContextMenuItem("command", text="Delete", command=lambda: print("Delete")),
]

btn = bs.DropdownButton(app, text="File", items=items)
btn.on_item_click(lambda info: print(info["text"]))
btn.pack(padx=20, pady=20)

app.mainloop()