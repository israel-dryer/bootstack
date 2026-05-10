import bootstack as bs

app = bs.App()

frame = bs.PackFrame(app, padding=16, gap=8, direction="horizontal").pack()

# standard
bs.MenuButton(frame, text="Menu", accent="primary").pack()
bs.MenuButton(frame, text="Menu", accent="primary", variant="outline").pack()

# with icon
bs.MenuButton(frame, icon="list",  icon_only=True, density="compact").pack()
bs.MenuButton(frame, text="View",  icon="eye",     density="compact").pack()

app.mainloop()