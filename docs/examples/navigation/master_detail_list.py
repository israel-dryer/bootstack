"""Master–detail (list) — a list drives a detail view (an email inbox).

``list_nav`` turns each record into a sidebar row (its ``title`` / ``text`` /
``icon``); ``@shell.detail`` renders the body for the selected record, received as
a dict. The first message is selected automatically — no ``navigate`` needed. The
inbox → read-the-message flow is the archetypal master–detail screen.
"""
import bootstack as bs
from bootstack.data import MemoryDataSource

inbox = MemoryDataSource().load([
    {"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "envelope",
     "body": "Hi — can we move the roadmap review to Thursday? Thanks, Dana"},
    {"id": 2, "title": "GitHub", "text": "[bootstack] PR #135 merged", "icon": "envelope-open",
     "body": "Your pull request was merged into main."},
    {"id": 3, "title": "Sam Okonkwo", "text": "Lunch tomorrow?", "icon": "envelope",
     "body": "Want to grab lunch tomorrow around noon?"},
    {"id": 4, "title": "Billing", "text": "Your receipt for June", "icon": "envelope-open",
     "body": "Thanks for your payment. Your receipt is attached."},
])

with bs.AppShell(title="Mail", size=(900, 580)) as shell:
    shell.commandbar.add_button(icon="pencil-square", label="Compose", on_click=lambda: None)
    shell.commandbar.add_spacer()
    shell.commandbar.add_theme_toggle()

    shell.list_nav(inbox, chevron=True)

    @shell.detail
    def read(message):
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
            bs.Label(message["text"], font="heading-lg")
            bs.Label(f"From {message['title']}", font="caption")
            bs.Separator(fill="x")
            bs.Label(message["body"])

shell.run()
