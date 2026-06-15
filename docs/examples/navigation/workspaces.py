"""Workspaces — multiple sections behind an icon rail (a mail + calendar suite).

Each ``add_workspace`` adds a rail icon and its own sidebar, authored with the
same page API — and each can use a *different* provider. Here Mail is a
master–detail list, Calendar is static pages, and Contacts is another list: the
rail appears automatically with more than one workspace. ``add_footer_workspace``
pins Settings to the rail bottom; ``navigate(workspace, page)`` jumps to a page.
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

with bs.AppShell(title="Workspace", size=(980, 620)) as shell:
    shell.commandbar.add_spacer()
    shell.commandbar.add_theme_toggle()

    # Mail — a master–detail list.
    with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
        ws.list_nav(inbox, chevron=True)

        @ws.detail
        def read(message):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label(message["text"], font="heading-lg")
                bs.Label(f"From {message['title']}", font="caption")
                bs.Separator()
                bs.Label(message["body"])

    # Calendar — static pages.
    with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
        with ws.add_page("today", text="Today", icon="calendar-day"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
                bs.Label("Today", font="heading-lg")
                bs.Label("No events.")
        with ws.add_page("week", text="Week", icon="calendar-week"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
                bs.Label("This week", font="heading-lg")

    # Contacts — another list.
    with shell.add_workspace("contacts", text="Contacts", icon="people") as ws:
        ws.list_nav(contacts, chevron=True)

        @ws.detail
        def card(person):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label(person["title"], font="heading-lg")
                bs.Label(person["text"], font="caption")
                bs.Label(f"Phone: {person['phone']}")

    with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
        with ws.add_page("general", text="General", icon="sliders"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
                bs.Label("Settings", font="heading-lg")

    # Mail is the first workspace, so it opens active with its first message
    # selected — no explicit navigate needed.

shell.run()
