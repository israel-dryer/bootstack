import bootstack as bs

app = bs.App(title="Custom Sidebar", minsize=(800, 500))

# Sidebar
sidebar = bs.Frame(app, padding=10, width=200)
sidebar.pack(side="left", fill="y")

# Content
stack = bs.PageStack(app)
stack.pack(side="left", fill="both", expand=True)

# Pages
for key in ["dashboard", "users", "settings"]:
    page = stack.add(key, padding=20)
    bs.Label(page, text=key.title(), font="heading-xl").pack(anchor="w")

# Navigation buttons with active tracking
nav_buttons = {}

for label, key in [("Dashboard", "dashboard"), ("Users", "users"), ("Settings", "settings")]:
    btn = bs.Button(
        sidebar, text=label, width=20,
        accent="secondary", variant="outline",
        command=lambda k=key: stack.navigate(k),
    )
    btn.pack(fill="x", pady=2)
    nav_buttons[key] = btn

def on_page_changed(event):
    current = event.data.get("page")
    for key, btn in nav_buttons.items():
        if key == current:
            btn.configure(accent="primary", variant=None)
        else:
            btn.configure(accent="secondary", variant="outline")

stack.on_page_changed(on_page_changed)
stack.navigate("dashboard")

app.mainloop()