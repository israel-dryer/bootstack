import bootstack as bs

app = bs.App(title="Editor", minsize=(900, 600))

def new_file(): pass
def open_file(): pass
def undo(): pass
def redo(): pass
def show_help(): pass

bar = bs.MenuBar(app)
bar.pack(fill="x")

bar.add_menu("File", items=[
    bs.ContextMenuItem("command", text="New",  icon="file-plus",    command=new_file),
    bs.ContextMenuItem("command", text="Open", icon="folder2-open", command=open_file),
    bs.ContextMenuItem("separator"),
    bs.ContextMenuItem("command", text="Exit", icon="x-circle",     command=app.destroy),
])

bar.add_menu("Edit", items=[
    bs.ContextMenuItem("command", text="Undo", icon="arrow-counterclockwise", command=undo),
    bs.ContextMenuItem("command", text="Redo", icon="arrow-clockwise",        command=redo),
])

bar.add_button("Help", icon="question-circle", region="after", command=show_help)

app.mainloop()