import bootstack as bs

TEAM = [
    {"id": 1, "title": "Alice Johnson",  "text": "Engineering lead", "icon": "person-fill"},
    {"id": 2, "title": "Bob Smith",      "text": "Product manager",  "icon": "person-fill"},
    {"id": 3, "title": "Carol Williams", "text": "Design director",  "icon": "person-fill"},
    {"id": 4, "title": "David Brown",    "text": "Data scientist",   "icon": "person-fill"},
    {"id": 5, "title": "Eva Martinez",   "text": "DevOps engineer",  "icon": "person-fill"},
]

ALERTS = [
    {"id": 1, "title": "Build passed",      "text": "main · 3 min ago",   "icon": "check-circle-fill"},
    {"id": 2, "title": "PR review ready",   "text": "feat/auth · 12 min", "icon": "git-pull-request"},
    {"id": 3, "title": "Deployment done",   "text": "production · 1 hr",  "icon": "rocket-takeoff-fill"},
    {"id": 4, "title": "Test suite failed", "text": "staging · 2 hr ago", "icon": "x-circle-fill"},
    {"id": 5, "title": "Lint warnings",     "text": "feat/ui · 4 hr ago", "icon": "exclamation-triangle"},
]

SIMPLE = [{"id": i, "text": f"Option {i}"} for i in range(1, 10)]


def hero():
    with bs.App(title="ListView", size=(400, 340), padding=20) as app:
        bs.ListView(items=TEAM, grow=True, horizontal="stretch")
    app.run()


def selection():
    with bs.App(title="ListView — Selection", size=(400, 340), padding=20) as app:
        lv = bs.ListView(
            items=SIMPLE,
            selection_mode="multi",
            show_selection_controls=True,
            accent="primary",
            grow=True, horizontal="stretch",
        )
    for item_id in (1, 3, 5):
        lv.data_source.select(item_id)
    lv.reload()
    app.run()


def features():
    with bs.App(title="ListView — Features", size=(400, 340), padding=20) as app:
        bs.ListView(items=ALERTS, show_chevron=True, allow_remove=True, grow=True, horizontal="stretch")
    app.run()


def density():
    with bs.App(title="ListView — Density", size=(400, 340), padding=20) as app:
        bs.ListView(items=SIMPLE, striped=True, density="compact", grow=True, horizontal="stretch")
    app.run()


SCENES = {
    "hero":      hero,
    "selection": selection,
    "features":  features,
    "density":   density,
}

if __name__ == '__main__':
    hero()