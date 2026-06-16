"""Single-tier app — a flat list of top-level destinations (an analytics dashboard).

Each ``add_page`` registers a sidebar item and its content together; the first
``navigate`` picks the starting page. With one set of pages no rail appears — this
is the everyday "sidebar app" shape.
"""
import bootstack as bs

with bs.AppShell(title="Acme Analytics", size=(900, 580)) as shell:
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_separator()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        bar.add_button(icon="search", on_click=lambda: None)
        bar.add_theme_toggle()

    with shell.add_page("overview", text="Overview", icon="speedometer2"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
            bs.Label("Overview", font="heading-lg")
            with bs.Grid(columns=3, gap=12, fill="x", sticky_items="ew"):
                for label, value in (("Revenue", "$48.2k"), ("Orders", "1,204"), ("Visitors", "18.9k")):
                    with bs.Card(padding=16, gap=4):
                        bs.Label(label, font="caption")
                        bs.Label(value, font="heading-md")

    with shell.add_page("reports", text="Reports", icon="bar-chart"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Reports", font="heading-lg")
            bs.Label("Build and schedule reports.")

    with shell.add_page("customers", text="Customers", icon="people"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Customers", font="heading-lg")
            bs.Label("1,204 active accounts.")

    with shell.add_footer_page("settings", text="Settings", icon="gear"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Settings", font="heading-lg")

    shell.navigate("overview")

shell.run()
