"""Grouped sidebar — pages chunked into labeled sections (a Settings window).

``nav.add_header`` adds a quiet section label and ``nav.add_divider`` a divider;
the pages between read as a group. Each page IS a column, so its ``padding`` /
``gap`` go on ``add_page`` — no inner wrapper. Settings screens are the canonical
case: related panes gathered under Account, Notifications, Advanced. Group
*consistently*: everything under a header.
"""
import bootstack as bs

with bs.AppShell(title="Settings", size=(860, 580)) as shell:
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_divider()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        bar.add_button(icon="search", on_click=lambda: None)
        bar.add_theme_toggle()

    with shell.page_nav() as nav:
        nav.add_header("Account")
        with nav.add_page("profile", text="Profile", icon="person", padding=20, gap=8):
            bs.Label("Profile", font="heading-lg")
            bs.Label("Your name, avatar, and bio.")
        with nav.add_page("security", text="Security", icon="shield-lock", padding=20, gap=8):
            bs.Label("Security", font="heading-lg")
            bs.Label("Password and two-factor authentication.")

        nav.add_header("Notifications")
        with nav.add_page("email", text="Email", icon="envelope", padding=20, gap=8):
            bs.Label("Email notifications", font="heading-lg")
        with nav.add_page("push", text="Push", icon="bell", padding=20, gap=8):
            bs.Label("Push notifications", font="heading-lg")

        nav.add_header("Advanced")
        with nav.add_page("developer", text="Developer", icon="terminal", padding=20, gap=8):
            bs.Label("Developer options", font="heading-lg")

    shell.navigate("profile")

shell.run()