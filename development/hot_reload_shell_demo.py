"""Hot-reload demo (AppShell).

Run it live:   bootstack dev development/hot_reload_shell_demo.py

Navigate to a page (e.g. Settings), then edit a page's contents or add a new
`nav.add_page(...)` and save — the shell rebuilds in place and keeps you on the
page you were viewing (the route is preserved across the reload).
"""
import bootstack as bs

with bs.AppShell(title="Hot Reload Shell") as shell:
    with shell.add_toolbar() as tb:
        tb.add_sidebar_toggle()
        tb.add_spacer()
        tb.add_theme_toggle()

    with shell.page_nav() as nav:
        with nav.add_page("home", text="Home", icon="house"):
            bs.Label("Home", font="heading-lg")
            bs.Label("Edit me and save.")
        with nav.add_page("settings", text="Settings", icon="gear"):
            bs.Label("Settings", font="heading-lg")
            bs.Label("Navigate here, then save — you stay on this page.")

    shell.navigate("home")

shell.run()
