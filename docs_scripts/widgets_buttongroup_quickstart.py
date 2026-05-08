import bootstack as bs

app = bs.App()

bg = bs.ButtonGroup(app)
bg.pack(padx=20, pady=20)

bg.add(text="Cut",   icon="scissors",  command=lambda: print("Cut"))
bg.add(text="Copy",  icon="copy",      command=lambda: print("Copy"))
bg.add(text="Paste", icon="clipboard", command=lambda: print("Paste"))

app.mainloop()