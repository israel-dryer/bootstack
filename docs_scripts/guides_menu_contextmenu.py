import bootstack as bs

app = bs.App(size=(200, 200))
frame = bs.PackFrame(app).pack(fill="both", expand=True)

def refresh(): pass
def copy_path(): pass
def show_props(): pass

ctx = bs.ContextMenu(frame, trigger="right-click")
ctx.add_command(text="Refresh",   icon="arrow-clockwise", command=refresh)
ctx.add_command(text="Copy path", icon="copy",            command=copy_path)
ctx.add_separator()
ctx.add_command(text="Properties", icon="gear",           command=show_props)

app.mainloop()