"""Grouped sidebar — pages chunked into labeled sections (a Settings window).

``add_header`` adds a quiet section label and ``add_separator`` a divider; the
pages between read as a group. Settings screens are the canonical case — related
panes gathered under Account, Notifications, Advanced. Group *consistently*:
everything under a header, not loose items sprinkled among sections.
"""
import bootstack as bs

with bs.AppShell(title="Settings", size=(860, 580)) as shell:
    shell.commandbar.add_label("Settings", font="heading-md")
    shell.commandbar.add_spacer()
    shell.commandbar.add_theme_toggle()

    shell.add_header("Account")
    with shell.add_page("profile", text="Profile", icon="person"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Profile", font="heading-lg")
            bs.Label("Your name, avatar, and bio.")
    with shell.add_page("security", text="Security", icon="shield-lock"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Security", font="heading-lg")
            bs.Label("Password and two-factor authentication.")

    shell.add_header("Notifications")
    with shell.add_page("email", text="Email", icon="envelope"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Email notifications", font="heading-lg")
    with shell.add_page("push", text="Push", icon="bell"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Push notifications", font="heading-lg")

    shell.add_header("Advanced")
    with shell.add_page("developer", text="Developer", icon="terminal"):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Developer options", font="heading-lg")

    shell.navigate("profile")

shell.run()
