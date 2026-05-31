import bootstack as bs

with bs.AppShell(title="My App") as shell:
    with shell.add_page("home", text="Home", icon="house"):
        with bs.VStack(padding=20, gap=8):
            bs.Label("Welcome!", font="heading-lg")
            bs.Label("Select a page from the sidebar.", accent="secondary")

    with shell.add_page("docs", text="Documents", icon="file-earmark-text"):
        with bs.VStack(padding=20, gap=8):
            bs.Label("Your documents.", font="heading-lg")

    shell.navigate("home")

shell.run()
