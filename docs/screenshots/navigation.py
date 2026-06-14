"""Hero screenshots for the navigation-patterns articles.

One scene per pattern, mirroring docs/examples/navigation/*.py. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py navigation

Each captures the full window (rail/sidebar/content/status bands).
"""
import bootstack as bs
from bootstack.data import MemoryDataSource


def single_tier():
    with bs.AppShell(title="Acme Analytics", size=(820, 520)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_label("Acme Analytics", font="heading-md")
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        with shell.add_page("overview", text="Overview", icon="speedometer2"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label("Overview", font="heading-lg")
                with bs.Grid(columns=3, gap=12, fill="x", sticky_items="ew"):
                    for label, value in (("Revenue", "$48.2k"), ("Orders", "1,204"), ("Visitors", "18.9k")):
                        with bs.Card(padding=16, gap=4):
                            bs.Label(label, font="caption")
                            bs.Label(value, font="heading-md")
        with shell.add_page("reports", text="Reports", icon="bar-chart"):
            bs.Label("Reports", font="heading-lg")
        with shell.add_page("customers", text="Customers", icon="people"):
            bs.Label("Customers", font="heading-lg")
        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            bs.Label("Settings", font="heading-lg")
        shell.navigate("overview")
    shell.run()


def grouped_sidebar():
    with bs.AppShell(title="Settings", size=(820, 520)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_label("Settings", font="heading-md")
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        shell.add_header("Account")
        with shell.add_page("profile", text="Profile", icon="person"):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
                bs.Label("Profile", font="heading-lg")
                bs.Label("Your name, avatar, and bio.")
        with shell.add_page("security", text="Security", icon="shield-lock"):
            bs.Label("Security", font="heading-lg")
        shell.add_header("Notifications")
        with shell.add_page("email", text="Email", icon="envelope"):
            bs.Label("Email", font="heading-lg")
        with shell.add_page("push", text="Push", icon="bell"):
            bs.Label("Push", font="heading-lg")
        shell.add_header("Advanced")
        with shell.add_page("developer", text="Developer", icon="terminal"):
            bs.Label("Developer", font="heading-lg")
        shell.navigate("profile")
    shell.run()


def master_detail_list():
    inbox = MemoryDataSource().load([
        {"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "envelope",
         "body": "Hi — can we move the roadmap review to Thursday? Thanks, Dana"},
        {"id": 2, "title": "GitHub", "text": "[bootstack] PR #135 merged", "icon": "envelope-open",
         "body": "Your pull request was merged into main."},
        {"id": 3, "title": "Sam Okonkwo", "text": "Lunch tomorrow?", "icon": "envelope",
         "body": "Want to grab lunch tomorrow around noon?"},
    ])
    with bs.AppShell(title="Mail", size=(820, 520)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_button(icon="pencil-square", label="Compose", on_click=lambda: None)
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        shell.list_nav(inbox, chevron=True)

        @shell.detail
        def read(message):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label(message["text"], font="heading-lg")
                bs.Label(f"From {message['title']}", font="caption")
                bs.Separator(fill="x")
                bs.Label(message["body"])
    shell.run()


def master_detail_tree():
    tree_nodes = [
        {"label": "src", "icon": "folder", "children": [
            {"label": "app.py", "icon": "filetype-py", "kind": "Python source", "size": "4.2 KB"},
            {"label": "utils.py", "icon": "filetype-py", "kind": "Python source", "size": "1.8 KB"},
        ]},
        {"label": "tests", "icon": "folder", "children": [
            {"label": "test_app.py", "icon": "filetype-py", "kind": "Python source", "size": "2.0 KB"},
        ]},
        {"label": "docs", "icon": "folder", "children": [
            {"label": "README.md", "icon": "filetype-md", "kind": "Markdown", "size": "920 B"},
        ]},
        {"label": "LICENSE", "icon": "file-earmark", "kind": "Text", "size": "1.1 KB"},
    ]
    with bs.AppShell(title="Files", size=(820, 520)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_label("Project", font="heading-md")
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        tree = shell.tree_nav(nodes=tree_nodes, placeholder="Select a file")

        @shell.detail
        def show(node):
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                bs.Label(node["text"], font="heading-lg")
                bs.Label(node.get("kind", ""), font="caption")
                if node.get("size"):
                    bs.Label(f"Size: {node['size']}")

        tree.expand_all()
        app = tree.find(lambda node: node.label == "app.py")
        if app is not None:
            tree.select(app)
    shell.run()


def workspaces():
    inbox = MemoryDataSource().load([
        {"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "envelope", "body": "Can we move it to Thursday?"},
        {"id": 2, "title": "Billing", "text": "Your receipt for June", "icon": "envelope-open", "body": "Thanks for your payment."},
    ])
    with bs.AppShell(title="Workspace", size=(900, 560)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
            ws.list_nav(inbox, chevron=True)

            @ws.detail
            def read(message):
                with bs.VStack(fill="both", expand=True, anchor_items="w", gap=12, padding=20):
                    bs.Label(message["text"], font="heading-lg")
                    bs.Label(f"From {message['title']}", font="caption")
                    bs.Separator()
                    bs.Label(message["body"])
        with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
            with ws.add_page("today", text="Today", icon="calendar-day"):
                bs.Label("Today", font="heading-lg")
        with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
            with ws.add_page("general", text="General", icon="sliders"):
                bs.Label("Settings", font="heading-lg")
    shell.run()


def custom_sidebar():
    products = [
        {"name": "Wireless Mouse", "category": "Electronics", "price": 24},
        {"name": "Desk Lamp", "category": "Home", "price": 39},
        {"name": "Mechanical Keyboard", "category": "Electronics", "price": 89},
    ]
    with bs.AppShell(title="Shop", size=(820, 520)) as shell:
        shell._capture_full_window = True
        shell.commandbar.add_label("Shop", font="heading-md")
        shell.commandbar.add_spacer()
        shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)
        category = bs.Signal("All")
        max_price = bs.Signal(100)
        results = bs.Signal("")

        def recompute(*_):
            lines = [f"{p['name']} — ${p['price']}" for p in products
                     if (category() == "All" or p["category"] == category()) and p["price"] <= max_price()]
            results.set("\n".join(lines) if lines else "No products match.")

        with shell.panel():
            with bs.VStack(fill="x", anchor_items="w", gap=12, padding=16):
                bs.Label("Filters", font="heading-md")
                bs.Label("Category", font="caption")
                bs.SelectButton(options=["All", "Electronics", "Home"], signal=category)
                bs.Label("Max price", font="caption")
                bs.Slider(min_value=10, max_value=100, signal=max_price)
        with shell.content:
            with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
                bs.Label("Results", font="heading-lg")
                bs.Label(textsignal=results)
        category.subscribe(recompute)
        max_price.subscribe(recompute)
        recompute()
    shell.run()


SCENES = {
    "single-tier": single_tier,
    "grouped-sidebar": grouped_sidebar,
    "master-detail-list": master_detail_list,
    "master-detail-tree": master_detail_tree,
    "workspaces": workspaces,
    "custom-sidebar": custom_sidebar,
}
