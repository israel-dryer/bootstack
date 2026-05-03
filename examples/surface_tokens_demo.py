"""Demo: Surface Tokens with GridFrame App Shell

Demonstrates the new semantic surface tokens for container backgrounds:
- content, content[1], content[2] - main content areas
- chrome, chrome[1] - UI chrome (sidebars, toolbars)
- overlay, overlay[2], overlay[3] - floating elements
- titlebar - window title bars
"""

import bootstack as bs


def create_demo():
    app = bs.App(title="Surface Tokens Demo", size=(900, 600), theme="dark")

    # Main app shell using GridFrame
    shell = bs.GridFrame(
        app,
        columns=["200px", "1fr"],
        rows=["48px", "1fr", "32px"],
    )
    shell.pack(fill="both", expand=True)

    # ===== Titlebar (row 0, spans both columns) =====
    titlebar = bs.Frame(shell, surface="titlebar", padding=10)
    titlebar.grid(row=0, column=0, columnspan=2, sticky="nsew")
    bs.Separator(shell).grid(row=0, column=0, columnspan=2, sticky='wes')

    bs.Label(
        titlebar,
        text="App Shell with Surface Tokens",
        font="heading",
    ).pack(side="left")

    bs.Button(
        titlebar,
        text="Toggle Theme",
        variant="ghost",
        command=bs.toggle_theme,
    ).pack(side="right")

    # ===== Sidebar (row 1, column 0) =====
    sidebar = bs.Frame(shell, surface="chrome", padding=10)
    sidebar.grid(row=1, column=0, sticky="nsew")

    bs.Label(sidebar, text="Navigation", font="heading-sm").pack(anchor="w", pady=(0, 10))

    nav_items = ["Dashboard", "Projects", "Tasks", "Reports", "Settings"]
    for item in nav_items:
        bs.Button(
            sidebar,
            text=item,
            variant="ghost",
            width=18,
        ).pack(fill="x", pady=2)

    # Nested chrome[1] panel
    bs.Separator(sidebar).pack(fill="x", pady=15)
    bs.Label(sidebar, text="Quick Stats", font="caption").pack(anchor="w")

    stats_panel = bs.Frame(sidebar, surface="chrome[1]", padding=8)
    stats_panel.pack(fill="x", pady=5)
    bs.Label(stats_panel, text="Active: 12").pack(anchor="w")
    bs.Label(stats_panel, text="Pending: 5").pack(anchor="w")

    # ===== Main Content Area (row 1, column 1) =====
    main = bs.Frame(shell, surface="content", padding=15)
    main.grid(row=1, column=1, sticky="nsew")

    bs.Label(main, text="Main Content (surface='content')", font="heading-sm").pack(anchor="w")
    bs.Label(
        main,
        text="This is the base content area. Cards and panels use elevated surfaces.",
    ).pack(anchor="w", pady=(5, 15))

    # Cards row using content[1]
    cards_row = bs.PackFrame(main, direction="horizontal", gap=15)
    cards_row.pack(fill="x")

    for i, title in enumerate(["Overview", "Analytics", "Activity"]):
        card = bs.Frame(cards_row, surface="content[1]", padding=15)
        card.pack(side="left", fill="both", expand=True)

        bs.Label(card, text=title, font="heading-sm").pack(anchor="w")
        bs.Label(card, text=f"Card using surface='content[1]'").pack(anchor="w", pady=5)

        # Nested content[2] for inset areas
        inset = bs.Frame(card, surface="content[2]", padding=8)
        inset.pack(fill="x", pady=(10, 0))
        bs.Label(inset, text="Inset area (content[2])").pack()

    # Overlay examples section
    bs.Separator(main).pack(fill="x", pady=20)
    bs.Label(main, text="Overlay Surface Examples", font="heading-sm").pack(anchor="w")

    overlay_row = bs.PackFrame(main, direction="horizontal", gap=15)
    overlay_row.pack(fill="x", pady=10)

    overlay_examples = [
        ("overlay", "Menus/Dropdowns"),
        ("overlay[2]", "Dialogs"),
        ("overlay[3]", "Tooltips/Toasts"),
    ]

    for surface, desc in overlay_examples:
        box = bs.Frame(overlay_row, surface=surface, padding=12)
        box.pack(side="left", fill="both", expand=True)
        bs.Label(box, text=desc, font="bold").pack()
        bs.Label(box, text=f"surface='{surface}'").pack()

    # ===== Status Bar (row 2, spans both columns) =====
    statusbar = bs.Frame(shell, surface="chrome[1]", padding=(10, 5))
    statusbar.grid(row=2, column=0, columnspan=2, sticky="nsew")

    bs.Label(statusbar, text="Ready").pack(side="left")
    bs.Label(statusbar, text="surface='chrome[1]'").pack(side="right")

    app.mainloop()


if __name__ == "__main__":
    create_demo()
