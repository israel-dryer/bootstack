"""Custom sidebar — a bespoke sidebar the providers can't express (search filters).

``panel()`` claims the sidebar as a blank container you fill with any widgets, and
you drive the content area yourself via ``shell.content``. A faceted filter
sidebar — category, price, rating — feeding a results area is the classic case:
it isn't navigation, so none of the nav providers fit. Reach for ``panel()`` only
when ``add_page`` / ``list_nav`` / ``tree_nav`` cannot express your sidebar.
"""
import bootstack as bs

PRODUCTS = [
    {"name": "Wireless Mouse", "category": "Electronics", "price": 24},
    {"name": "Desk Lamp", "category": "Home", "price": 39},
    {"name": "Mechanical Keyboard", "category": "Electronics", "price": 89},
    {"name": "Throw Pillow", "category": "Home", "price": 19},
    {"name": "USB-C Hub", "category": "Electronics", "price": 45},
]

with bs.AppShell(title="Shop", size=(900, 580)) as shell:
    shell.commandbar.add_label("Shop", font="heading-md")
    shell.commandbar.add_spacer()
    shell.commandbar.add_button(icon="circle-half", on_click=bs.toggle_theme)

    category = bs.Signal("All")
    max_price = bs.Signal(100)
    results = bs.Signal("")

    def recompute(*_):
        matches = [
            p for p in PRODUCTS
            if (category() == "All" or p["category"] == category())
            and p["price"] <= max_price()
        ]
        lines = [f"{p['name']} — ${p['price']}" for p in matches]
        results.set("\n".join(lines) if lines else "No products match.")

    # A bespoke filter sidebar — not navigation, so panel() is the right tool.
    with shell.panel():
        with bs.VStack(fill="x", anchor_items="w", gap=12, padding=16):
            bs.Label("Filters", font="heading-md")
            bs.Label("Category", font="caption")
            bs.SelectButton(options=["All", "Electronics", "Home"], signal=category)
            bs.Label("Max price", font="caption")
            bs.Slider(min_value=10, max_value=100, signal=max_price)

    # Drive the content region by hand from the filter signals.
    with shell.content:
        with bs.VStack(fill="both", expand=True, anchor_items="w", gap=8, padding=20):
            bs.Label("Results", font="heading-lg")
            bs.Label(textsignal=results)

    category.subscribe(recompute)
    max_price.subscribe(recompute)
    recompute()

shell.run()
