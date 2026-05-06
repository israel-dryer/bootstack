import bootstack as bs

shell = bs.AppShell(title="My App", minsize=(1000, 650))

# Each add_page() creates a nav item and returns a Frame for content
home = shell.add_page("home", text="Home", icon="house")
bs.Label(home, text="Welcome!").pack(padx=20, pady=20)

docs = shell.add_page("docs", text="Documents", icon="file-earmark-text")
bs.Label(docs, text="Your documents.").pack(padx=20, pady=20)

# Toolbar buttons appear on the right side
shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)

shell.mainloop()