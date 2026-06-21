"""Hero screenshots for the navigation-patterns articles.

One scene per pattern, mirroring docs/examples/navigation/*.py. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py navigation

Each captures the full window (rail/sidebar/content/status bands).
"""
import bootstack as bs
from bootstack.data import MemoryDataSource


def _menu_toolbar(shell, *, search=True):
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file:
            file.add_action("New", shortcut="Mod+N", on_click=lambda: None)
            file.add_action("Open", shortcut="Mod+O", on_click=lambda: None)
            file.add_divider()
            file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view:
            view.add_action("Refresh", shortcut="Mod+R", on_click=lambda: None)
        bar.add_spacer()
        if search:
            bar.add_button(icon="search", on_click=lambda: None)
        bar.add_theme_toggle()


def single_tier():
    with bs.AppShell(title="Acme Analytics", size=(720, 460)) as shell:
        shell._capture_full_window = True
        _menu_toolbar(shell)
        with shell.page_nav() as nav:
            with nav.add_page("overview", text="Overview", icon="speedometer2", gap=12, padding=20):
                bs.Label("Overview", font="heading-lg")
                with bs.Grid(columns=3, gap=12, horizontal="stretch", horizontal_items="stretch"):
                    for label, value in (("Revenue", "$48.2k"), ("Orders", "1,204"), ("Visitors", "18.9k")):
                        with bs.Card(padding=16, gap=4):
                            bs.Label(label, font="caption")
                            bs.Label(value, font="heading-md")
            with nav.add_page("reports", text="Reports", icon="bar-chart", padding=20):
                bs.Label("Reports", font="heading-lg")
            with nav.add_page("customers", text="Customers", icon="people", padding=20):
                bs.Label("Customers", font="heading-lg")
            with nav.add_page("settings", text="Settings", icon="gear", pin_to_footer=True, padding=20):
                bs.Label("Settings", font="heading-lg")
        shell.navigate("overview")
    shell.run()


def grouped_sidebar():
    with bs.AppShell(title="Settings", size=(720, 460)) as shell:
        shell._capture_full_window = True
        _menu_toolbar(shell)
        with shell.page_nav() as nav:
            nav.add_header("Account")
            with nav.add_page("profile", text="Profile", icon="person", gap=8, padding=20):
                bs.Label("Profile", font="heading-lg")
                bs.Label("Your name, avatar, and bio.")
            with nav.add_page("security", text="Security", icon="shield-lock", padding=20):
                bs.Label("Security", font="heading-lg")
            nav.add_header("Notifications")
            with nav.add_page("email", text="Email", icon="envelope", padding=20):
                bs.Label("Email", font="heading-lg")
            with nav.add_page("push", text="Push", icon="bell", padding=20):
                bs.Label("Push", font="heading-lg")
            nav.add_header("Advanced")
            with nav.add_page("developer", text="Developer", icon="terminal", padding=20):
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
    with bs.AppShell(title="Mail", size=(720, 460)) as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New message", shortcut="Mod+N", on_click=lambda: None)
                file.add_divider()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            bar.add_button(icon="pencil-square", label="Compose", on_click=lambda: None)
            bar.add_button(icon="archive", on_click=lambda: None)
            bar.add_spacer()
            bar.add_theme_toggle()
        shell.list_nav(inbox, chevron=True)

        @shell.detail
        def read(message):
            with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
                bs.Label(message["text"], font="heading-lg")
                bs.Label(f"From {message['title']}", font="caption")
                bs.Divider(horizontal="stretch")
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
    with bs.AppShell(title="Files", size=(720, 460)) as shell:
        shell._capture_full_window = True
        _menu_toolbar(shell)
        tree = shell.tree_nav(nodes=tree_nodes, placeholder="Select a file")

        @shell.detail
        def show(node):
            with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
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
    with bs.Workbench(title="Workspace", size=(720, 460)) as shell:
        shell._capture_full_window = True
        _menu_toolbar(shell)
        with shell.add_workspace("mail", text="Mail", icon="envelope") as ws:
            ws.list_nav(inbox, chevron=True)

            @ws.detail
            def read(message):
                with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
                    bs.Label(message["text"], font="heading-lg")
                    bs.Label(f"From {message['title']}", font="caption")
                    bs.Divider()
                    bs.Label(message["body"])
        with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
            with ws.page_nav() as nav:
                with nav.add_page("today", text="Today", icon="calendar-day", padding=20):
                    bs.Label("Today", font="heading-lg")
        with shell.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True) as ws:
            with ws.page_nav() as nav:
                with nav.add_page("general", text="General", icon="sliders", padding=20):
                    bs.Label("Settings", font="heading-lg")
    shell.run()


def custom_sidebar():
    products = [
        {"name": "Wireless Mouse", "category": "Electronics", "price": 24},
        {"name": "Desk Lamp", "category": "Home", "price": 39},
        {"name": "Mechanical Keyboard", "category": "Electronics", "price": 89},
    ]
    with bs.AppShell(title="Shop", size=(720, 460)) as shell:
        shell._capture_full_window = True
        with shell.add_toolbar() as bar:
            with bar.add_menu("File") as file:
                file.add_action("New order", shortcut="Mod+N", on_click=lambda: None)
                file.add_divider()
                file.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
            bar.add_spacer()
            bar.add_button(icon="search", on_click=lambda: None)
            bar.add_button(icon="cart", on_click=lambda: None)
            bar.add_theme_toggle()
        category = bs.Signal("All")
        max_price = bs.Signal(100)
        results = bs.Signal("")

        def recompute(*_):
            lines = [f"{p['name']} — ${p['price']}" for p in products
                     if (category() == "All" or p["category"] == category()) and p["price"] <= max_price()]
            results.set("\n".join(lines) if lines else "No products match.")

        with shell.custom_nav():
            with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
                bs.Label("Filters", font="heading-md")
                bs.Label("Category", font="caption")
                bs.SelectButton(options=["All", "Electronics", "Home"], signal=category)
                bs.Label("Max price", font="caption")
                bs.Slider(min_value=10, max_value=100, signal=max_price)
        with shell.content:
            with bs.Column(horizontal_items="left", gap=8, padding=(16, 10)):
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