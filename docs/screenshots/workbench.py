"""Screenshots for the Workbench widget page.

The two-tier shell: a workspace rail + per-workspace sidebar + content. Two
scenes — the default icon-only rail (hero) and the labeled rail (rail-labels).
Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py workbench
"""
import bootstack as bs
from bootstack.data import MemoryDataSource

INBOX = [
    {"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "envelope",
     "body": "Hi — can we move the roadmap review to Thursday? Thanks, Dana"},
    {"id": 2, "title": "GitHub", "text": "[bootstack] PR #135 merged", "icon": "envelope-open",
     "body": "Your pull request was merged into main."},
    {"id": 3, "title": "Sam Okonkwo", "text": "Lunch tomorrow?", "icon": "envelope",
     "body": "Want to grab lunch tomorrow around noon?"},
]


def _suite(rail_labels):
    inbox = MemoryDataSource().load(INBOX)
    width = 860 if rail_labels else 800
    with bs.Workbench(title="Suite", size=(width, 540), nav_accent="primary",
                      rail_labels=rail_labels) as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
                file.add_divider()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            bar.add_spacer()
            bar.add_theme_toggle()

        # Mail — a master–detail list (opens active with its first message).
        with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
            ws.list_nav(inbox, chevron=True)

            @ws.detail
            def read(message):
                with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
                    bs.Label(message["text"], font="heading-lg")
                    bs.Label(f"From {message['title']}", font="caption")
                    bs.Divider(horizontal="stretch")
                    bs.Label(message["body"])

        # Calendar — a page nav.
        with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
            with ws.page_nav() as nav:
                with nav.add_page("today", text="Today", icon="calendar-day", padding=20):
                    bs.Label("Today", font="heading-lg")

        # Contacts — a page nav.
        with shell.add_workspace("contacts", text="Contacts", icon="people") as ws:
            with ws.page_nav() as nav:
                with nav.add_page("all", text="All contacts", icon="person-lines-fill", padding=20):
                    bs.Label("Contacts", font="heading-lg")

        # Settings — pinned to the rail bottom.
        with shell.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True) as ws:
            with ws.page_nav() as nav:
                with nav.add_page("general", text="General", icon="sliders", padding=20):
                    bs.Label("Settings", font="heading-lg")
    shell.run()


def hero():
    _suite(rail_labels=False)


def rail_labels():
    _suite(rail_labels=True)


SCENES = {
    "hero": hero,
    "rail-labels": rail_labels,
}