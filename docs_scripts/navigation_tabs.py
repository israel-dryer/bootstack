import bootstack as bs

app = bs.App(size=(300, 200))

notebook = bs.Notebook(app, accent="primary")

notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Create tabs
home = notebook.add(text="Home", key="home")
settings = notebook.add(text="Settings", key="settings")
about = notebook.add(text="About", key="about")

# Add content to each tab
bs.Label(home, text="Welcome to the application").pack(anchor="w")
bs.Label(settings, text="Configure your preferences here").pack(anchor="w")
bs.Label(about, text="Version 1.0").pack(anchor="w")

app.mainloop()