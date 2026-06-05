import bootstack as bs


def hero():
    with bs.App(title="SideNav", size=(680, 520), padding=0, gap=0) as app:
        with bs.HStack(fill="both", expand=True):
            nav = bs.SideNav(title="My App", fill="y")
            nav.add_item("home",   "Home",   icon="house")
            nav.add_item("inbox",  "Inbox",  icon="inbox")
            nav.add_separator()
            nav.add_header("Documents")
            nav.add_item("files",  "Files",  icon="folder")
            nav.add_item("images", "Images", icon="image")
            nav.add_group("archive", "Archive", icon="archive", expanded=True)
            nav.add_item("recent", "Recent", group="archive")
            nav.add_item("backup", "Backup", group="archive")
            nav.add_footer_item("settings", "Settings", icon="gear")
            nav.add_footer_item("help",     "Help",     icon="question-circle")
            nav.select("home")
            with bs.VStack(fill="both", expand=True, padding=24, gap=8):
                bs.Label("Content Area", font="heading-md")
                bs.Label("Select a navigation item from the sidebar.")
    app.run()


def compact():
    with bs.App(title="SideNav — Compact", size=(440, 420), padding=8, gap=0) as app:
        with bs.HStack(fill="both", expand=True):
            nav = bs.SideNav(title="My App", display_mode="compact", fill="y")
            nav.add_item("home",   "Home",     icon="house")
            nav.add_item("inbox",  "Inbox",    icon="inbox")
            nav.add_item("files",  "Files",    icon="folder")
            nav.add_item("images", "Images",   icon="image")
            nav.add_footer_item("settings", "Settings", icon="gear")
            nav.select("home")
            with bs.VStack(fill="both", expand=True, padding=24, gap=8):
                bs.Label("Content Area", font="heading-md")
                bs.Label("Compact mode — labels appear as tooltips.")
    app.run()


SCENES = {
    "hero":    hero,
    "compact": compact,
}
