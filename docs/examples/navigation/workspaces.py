"""Workspaces — multiple sections behind an icon rail (a mail + calendar suite).

A ``Workbench`` is the two-tier shell: each ``add_workspace`` adds a rail icon and
its own sidebar, and each workspace is a sidebar host authored with the same front
doors as an ``AppShell``. Here Mail is a master–detail list, Calendar is a page
nav, and Contacts is another list. ``pin_to_footer=True`` pins Settings to the
rail bottom; ``navigate(workspace, page)`` jumps to a page.
"""
import bootstack as bs
from bootstack.data import MemoryDataSource

inbox = MemoryDataSource().load([
    {"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "envelope", "body": "Can we move it to Thursday?"},
    {"id": 2, "title": "Billing", "text": "Your receipt for June", "icon": "envelope-open", "body": "Thanks for your payment."},
])
contacts = MemoryDataSource().load([
    {"id": 1, "title": "Dana Reyes", "text": "dana@acme.io", "icon": "person-circle", "phone": "555-0142"},
    {"id": 2, "title": "Sam Okonkwo", "text": "sam@acme.io", "icon": "person-circle", "phone": "555-0177"},
])

with bs.Workbench(title="Workspace", size=(980, 620)) as shell:
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

    # Mail — a master–detail list.
    with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
        ws.list_nav(inbox, chevron=True)

        @ws.detail
        def read(message):
            with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
                bs.Label(message["text"], font="heading-lg")
                bs.Label(f"From {message['title']}", font="caption")
                bs.Divider()
                bs.Label(message["body"])

    # Calendar — a page nav (authored pages).
    with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
        with ws.page_nav() as nav:
            with nav.add_page("today", text="Today", icon="calendar-day", padding=20, gap=8):
                bs.Label("Today", font="heading-lg")
                bs.Label("No events.")
            with nav.add_page("week", text="Week", icon="calendar-week", padding=20, gap=8):
                bs.Label("This week", font="heading-lg")

    # Contacts — another list.
    with shell.add_workspace("contacts", text="Contacts", icon="people") as ws:
        ws.list_nav(contacts, chevron=True)

        @ws.detail
        def card(person):
            with bs.Column(grow=True, horizontal="stretch", gap=12, padding=20):
                bs.Label(person["title"], font="heading-lg")
                bs.Label(person["text"], font="caption")
                bs.Label(f"Phone: {person['phone']}")

    with shell.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True) as ws:
        with ws.page_nav() as nav:
            with nav.add_page("general", text="General", icon="sliders", padding=20, gap=8):
                bs.Label("Settings", font="heading-lg")

    # Mail is the first workspace, so it opens active with its first message
    # selected — no explicit navigate needed.

shell.run()