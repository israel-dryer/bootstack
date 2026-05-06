import bootstack as bs

shell = bs.AppShell(title="Combined Navigation", minsize=(1000, 650))

# Simple page
home = shell.add_page("home", text="Home", icon="house")
bs.Label(home, text="Dashboard", font="heading-xl").pack(anchor="w", padx=20, pady=20)

# Page with tabs inside
settings = shell.add_page("settings", text="Settings", icon="gear")

tabs = bs.Notebook(settings)
tabs.pack(fill="both", expand=True)

general = tabs.add(text="General", key="general", padding=16)
bs.Label(general, text="General settings").pack(anchor="w")

advanced = tabs.add(text="Advanced", key="advanced")
bs.Label(advanced, text="Advanced options").pack(anchor="w")

shell.mainloop()