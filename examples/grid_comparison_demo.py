"""
Grid Comparison Demo

Demonstrates the difference between building a complex grid layout with:
1. Regular Frame + manual grid configuration
2. GridFrame with declarative configuration

Both produce the same visual result, but GridFrame requires less boilerplate.
"""

import bootstack as bs


def create_with_frame(parent: bs.Frame) -> bs.Frame:
    """Build a form layout using regular Frame with manual grid calls."""

    frame = bs.Frame(parent, padding=20)

    # Manual column configuration
    frame.columnconfigure(0, weight=0, minsize=100)  # Labels column
    frame.columnconfigure(1, weight=1, minsize=200)  # Inputs column
    frame.columnconfigure(2, weight=0, minsize=80)   # Actions column

    # Manual row configuration
    for i in range(7):
        frame.rowconfigure(i, weight=0, pad=6)

    # Header - manual row/column/sticky/columnspan
    header = bs.Label(frame, text="User Registration", font=("", 14, "bold"))
    header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

    # Row 1: Username
    bs.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", padx=(0, 10))
    username = bs.Entry(frame)
    username.grid(row=1, column=1, sticky="ew")
    bs.Button(frame, text="Check", accent="info", variant="outline").grid(row=1, column=2, sticky="ew", padx=(10, 0))

    # Row 2: Email
    bs.Label(frame, text="Email:").grid(row=2, column=0, sticky="e", padx=(0, 10))
    email = bs.Entry(frame)
    email.grid(row=2, column=1, sticky="ew")
    bs.Button(frame, text="Verify", accent="info", variant="outline").grid(row=2, column=2, sticky="ew", padx=(10, 0))

    # Row 3: Password
    bs.Label(frame, text="Password:").grid(row=3, column=0, sticky="e", padx=(0, 10))
    password = bs.Entry(frame, show="*")
    password.grid(row=3, column=1, columnspan=2, sticky="ew")

    # Row 4: Confirm Password
    bs.Label(frame, text="Confirm:").grid(row=4, column=0, sticky="e", padx=(0, 10))
    confirm = bs.Entry(frame, show="*")
    confirm.grid(row=4, column=1, columnspan=2, sticky="ew")

    # Row 5: Options (checkbuttons)
    bs.Label(frame, text="Options:").grid(row=5, column=0, sticky="ne", padx=(0, 10), pady=(5, 0))

    options_frame = bs.Frame(frame)
    options_frame.grid(row=5, column=1, columnspan=2, sticky="w")
    bs.CheckButton(options_frame, text="Subscribe to newsletter").pack(anchor="w")
    bs.CheckButton(options_frame, text="Accept terms and conditions").pack(anchor="w")

    # Row 6: Buttons
    buttons_frame = bs.Frame(frame)
    buttons_frame.grid(row=6, column=0, columnspan=3, sticky="e", pady=(15, 0))
    bs.Button(buttons_frame, text="Cancel", accent="secondary").pack(side="left", padx=(0, 10))
    bs.Button(buttons_frame, text="Register", accent="primary").pack(side="left")

    return frame


def create_with_gridframe(parent: bs.Frame) -> bs.GridFrame:
    """Build the same form layout using GridFrame with declarative config."""

    # Declare structure upfront: label column (100px min), input column (flex), action column (80px min)
    # sticky_items="ew" applies to all children by default
    # gap=(10, 6) provides consistent spacing automatically
    grid = bs.GridFrame(
        parent,
        columns=["100px", 1, "80px"],  # minsize for cols 0 and 2, weight=1 for col 1
        gap=(10, 6),
        padding=20,
        sticky_items="ew",  # Default sticky for all children
    )

    # Header - use grid() with overrides
    bs.Label(grid, text="User Registration", font=("", 14, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 10)
    )

    # Row 1: Username
    bs.Label(grid, text="Username:").grid(row=1, column=0, sticky="e")
    bs.Entry(grid).grid(row=1, column=1)  # Uses default "ew"
    bs.Button(grid, text="Check", accent="info", variant="outline").grid(row=1, column=2)

    # Row 2: Email
    bs.Label(grid, text="Email:").grid(row=2, column=0, sticky="e")
    bs.Entry(grid).grid(row=2, column=1)
    bs.Button(grid, text="Verify", accent="info", variant="outline").grid(row=2, column=2)

    # Row 3: Password
    bs.Label(grid, text="Password:").grid(row=3, column=0, sticky="e")
    bs.Entry(grid, show="*").grid(row=3, column=1, columnspan=2)

    # Row 4: Confirm Password
    bs.Label(grid, text="Confirm:").grid(row=4, column=0, sticky="e")
    bs.Entry(grid, show="*").grid(row=4, column=1, columnspan=2)

    # Row 5: Options
    bs.Label(grid, text="Options:").grid(row=5, column=0, sticky="ne", pady=(5, 0))

    options = bs.Frame(grid)  # Use plain Frame like the other example
    options.grid(row=5, column=1, columnspan=2, sticky="w")
    bs.CheckButton(options, text="Subscribe to newsletter").pack(anchor="w")
    bs.CheckButton(options, text="Accept terms and conditions").pack(anchor="w")

    # Row 6: Buttons
    buttons = bs.Frame(grid)  # Use plain Frame like the other example
    buttons.grid(row=6, column=0, columnspan=3, sticky="e", pady=(15, 0))
    bs.Button(buttons, text="Cancel", accent="secondary").pack(side="left", padx=(0, 10))
    bs.Button(buttons, text="Register", accent="primary").pack(side="left")

    return grid


def main():
    app = bs.App(title="Grid Comparison Demo", theme="cosmo", size=(900, 500))

    # Create a tabview to show both approaches side by side
    tabview = bs.TabView(app)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab 1: Regular Frame approach
    frame_tab = tabview.add("frame", text="Frame + grid()")
    frame_tab.configure(padding=10)

    info1 = bs.Label(
        frame_tab,
        text="Using regular Frame requires manual columnconfigure/rowconfigure calls,\n"
             "plus explicit padx/pady on each widget for consistent spacing.",
        foreground="gray",
    )
    info1.pack(anchor="w", pady=(0, 10))

    frame_example = create_with_frame(frame_tab)
    frame_example.pack(fill="both", expand=True)

    # Tab 2: GridFrame approach
    gridframe_tab = tabview.add("gridframe", text="GridFrame")
    gridframe_tab.configure(padding=10)

    info2 = bs.Label(
        gridframe_tab,
        text="Using GridFrame with grid(), column weights are declared upfront with columns=[...],\n"
             "gap=(10, 6) provides spacing, and sticky_items='ew' sets default alignment.",
        foreground="gray",
    )
    info2.pack(anchor="w", pady=(0, 10))

    gridframe_example = create_with_gridframe(gridframe_tab)
    gridframe_example.pack(fill="both", expand=True)

    # Code comparison panel at the bottom
    comparison = bs.LabelFrame(app, text="Code Comparison", padding=10)
    comparison.pack(fill="x", padx=10, pady=(0, 10))

    comparison_text = bs.Label(
        comparison,
        text=(
            "Frame + .grid(): columnconfigure(0, weight=0, minsize=100) × 3 columns\n"
            "                 rowconfigure(i, weight=0, pad=6) × 7 rows\n"
            "                 padx=(0, 10) + sticky='ew' on each widget\n\n"
            "GridFrame:       columns=['100px', 1, '80px'], gap=(10, 6), sticky_items='ew'\n"
            "                 Minsizes, weights, spacing, and sticky declared once."
        ),
        font=("Consolas", 9),
        justify="left",
    )
    comparison_text.pack(anchor="w")

    app.mainloop()


if __name__ == "__main__":
    main()
