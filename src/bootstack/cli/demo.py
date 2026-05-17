"""
Widget Gallery

An AppShell-based showcase of bootstack widgets, organized by category
to mirror the documentation structure. Each sidebar item opens a page
demonstrating a widget group.
"""

import bootstack as bs
from bootstack.constants import *
from bootstack.signals import Signal
from bootstack.widgets.composites.tabs.tabview import TabView


# =============================================================================
# Page builders — one per sidebar item
# =============================================================================


def _build_home_page(page):
    """Welcome / overview page."""
    bs.Label(
        page, text="bootstack", font="heading-xl[bold]",
    ).pack(anchor=W, padx=20, pady=(20, 4))

    bs.Label(
        page,
        text="Modern UI framework for Python",
        font="body",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 20))

    content = bs.LabelFrame(page, text="About This Gallery", padding=20)
    content.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 20))

    bs.Label(
        content,
        text=(
            "Browse the sidebar to explore bootstack widgets by category.\n\n"
            "Each page demonstrates a group of related widgets with\n"
            "color variants, style options, and interactive examples.\n\n"
            "Use the theme toggle in the toolbar or visit the Theme\n"
            "page to try different themes."
        ),
    ).pack(expand=YES)


# -- Typography ---------------------------------------------------------------


def _build_typography_page(page):
    """Font tokens and modifiers showcase."""
    bs.Label(
        page, text="Typography", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Semantic font tokens for consistent text styling.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Font tokens
    group1 = bs.LabelFrame(page, text="Font Tokens", padding=15)
    group1.pack(fill=X, padx=20, pady=(0, 10))

    fonts = [
        ("display-xl", "Display XL"),
        ("display-lg", "Display LG"),
        ("heading-xl", "Heading XL"),
        ("heading-lg", "Heading LG"),
        ("heading-md", "Heading MD"),
        ("heading-sm", "Heading SM"),
        ("body-xl", "Body XL"),
        ("body-lg", "Body LG"),
        ("body", "Body (default)"),
        ("body-sm", "Body SM"),
        ("label", "Label"),
        ("caption", "Caption"),
        ("code", "Code"),
    ]
    for i, (token, desc) in enumerate(fonts):
        group1.columnconfigure(0, weight=0, minsize=200)
        group1.columnconfigure(1, weight=1)
        bs.Label(group1, text=desc, font=token).grid(row=i, column=0, sticky=W, pady=2)
        bs.Label(group1, text=f"font=\"{token}\"", font="code", accent="secondary").grid(row=i, column=1, sticky=W, pady=2)

    # Font modifiers
    group2 = bs.LabelFrame(page, text="Font Modifiers", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    modifiers = [
        ("body[bold]", "Bold"),
        ("body[italic]", "Italic"),
        ("body[bold][italic]", "Bold Italic"),
        ("body[underline]", "Underline"),
        ("heading-md[bold]", "Heading Bold"),
    ]
    group2.columnconfigure(0, weight=0, minsize=200)
    group2.columnconfigure(1, weight=1)
    for i, (token, desc) in enumerate(modifiers):
        bs.Label(group2, text=desc, font=token).grid(row=i, column=0, sticky=W, pady=2)
        bs.Label(group2, text=f"font=\"{token}\"", font="code", accent="secondary").grid(row=i, column=1, sticky=W, pady=2)


# -- Icons --------------------------------------------------------------------


def _build_icons_page(page):
    """Bootstrap Icons showcase."""
    bs.Label(
        page, text="Icons", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Bootstrap Icons available via the icon parameter.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Icon gallery
    group1 = bs.LabelFrame(page, text="Common Icons", padding=15)
    group1.pack(fill=X, padx=20, pady=(0, 10))

    icon_names = [
        "house", "gear", "person", "search", "bell",
        "envelope", "heart", "star", "trash", "pencil",
        "folder", "file-earmark-text", "download", "upload", "check-circle",
        "exclamation-triangle", "info-circle", "x-circle", "arrow-left", "arrow-right",
    ]
    icon_row = bs.Frame(group1)
    icon_row.pack(fill=X, pady=(0, 8))
    for i, name in enumerate(icon_names):
        if i > 0 and i % 10 == 0:
            icon_row = bs.Frame(group1)
            icon_row.pack(fill=X, pady=(0, 8))
        f = bs.Frame(icon_row)
        f.pack(side=LEFT, padx=6)
        bs.Label(f, icon=name, icon_only=True).pack()
        bs.Label(f, text=name, font="caption").pack()

    # Icon sizes
    group2 = bs.LabelFrame(page, text="Icon Sizes", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    size_row = bs.Frame(group2)
    size_row.pack(fill=X)
    for size in (12, 16, 20, 24, 32, 48):
        f = bs.Frame(size_row)
        f.pack(side=LEFT, padx=10)
        bs.Label(f, icon={"name": "star-fill", "size": size}, icon_only=True).pack()
        bs.Label(f, text=f"{size}px", font="caption").pack()

    # Icons in context
    group3 = bs.LabelFrame(page, text="Icons in Context", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    ctx_row = bs.Frame(group3)
    ctx_row.pack(fill=X, pady=(0, 8))
    bs.Button(ctx_row, text="Save", icon="save").pack(side=LEFT, padx=(0, 8))
    bs.Button(ctx_row, text="Delete", icon="trash", accent="danger").pack(side=LEFT, padx=(0, 8))
    bs.Button(ctx_row, text="Settings", icon="gear", accent="secondary").pack(side=LEFT, padx=(0, 8))
    bs.Button(ctx_row, icon="plus-lg", icon_only=True, accent="success").pack(side=LEFT, padx=(0, 8))
    bs.Button(ctx_row, icon="x-lg", icon_only=True, accent="danger").pack(side=LEFT)

    # Accent-colored icons
    group4 = bs.LabelFrame(page, text="Accent Colors on Icons", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    color_row = bs.Frame(group4)
    color_row.pack(fill=X)
    for color in ("primary", "secondary", "success", "info", "warning", "danger"):
        f = bs.Frame(color_row)
        f.pack(side=LEFT, padx=8)
        bs.Label(f, icon="heart-fill", icon_only=True, accent=color).pack()
        bs.Label(f, text=color, font="caption").pack()


# -- Actions ------------------------------------------------------------------


def _build_buttons_page(page):
    """Buttons, dropdown buttons, button groups."""
    bs.Label(
        page, text="Actions", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Buttons and button-like widgets for triggering actions.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Color variants
    group = bs.LabelFrame(page, text="Button — Color Variants", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    row = bs.Frame(group)
    row.pack(fill=X)
    for color in ("primary", "secondary", "success", "info", "warning", "danger"):
        bs.Button(row, text=color.title(), accent=color).pack(
            side=LEFT, padx=2, expand=YES, fill=X,
        )

    # Style variants
    group2 = bs.LabelFrame(page, text="Button — Style Variants", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    row2 = bs.Frame(group2)
    row2.pack(fill=X, pady=(0, 8))
    for variant_name in ("solid", "outline", "link", "ghost"):
        bs.Button(
            row2, text=variant_name.title(), accent="primary", variant=variant_name,
        ).pack(side=LEFT, padx=2, expand=YES, fill=X)

    row3 = bs.Frame(group2)
    row3.pack(fill=X)
    bs.Button(row3, text="Disabled Solid", accent="primary", state=DISABLED).pack(
        side=LEFT, padx=2, expand=YES, fill=X,
    )
    bs.Button(
        row3, text="Disabled Outline", accent="secondary",
        variant="outline", state=DISABLED,
    ).pack(side=LEFT, padx=2, expand=YES, fill=X)

    # DropdownButton
    group3 = bs.LabelFrame(page, text="DropdownButton", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    dd = bs.DropdownButton(group3, text="File", accent="primary")
    dd.pack(side=LEFT, padx=(0, 8))
    dd.add_command(text="New")
    dd.add_command(text="Open")
    dd.add_separator()
    dd.add_command(text="Exit")

    dd2 = bs.DropdownButton(
        group3, text="Edit", accent="secondary", variant="outline",
    )
    dd2.pack(side=LEFT, padx=(0, 8))
    dd2.add_command(text="Cut")
    dd2.add_command(text="Copy")
    dd2.add_command(text="Paste")

    # MenuButton
    mb = bs.MenuButton(group3, text="Options", accent="info")
    mb.pack(side=LEFT)
    menu = bs.Menu(mb, tearoff=0)
    menu.add_command(label="Settings")
    menu.add_command(label="Preferences")
    mb["menu"] = menu

    # ButtonGroup
    group4 = bs.LabelFrame(page, text="ButtonGroup", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    for accent, variant in [
        ("primary", "solid"), ("secondary", "outline"), ("success", "ghost"),
    ]:
        bg = bs.ButtonGroup(group4, accent=accent, variant=variant)
        bg.pack(side=LEFT, padx=(0, 12))
        bg.add(text="Cut", icon="scissors")
        bg.add(text="Copy", icon="copy")
        bg.add(text="Paste", icon="clipboard")


# -- Text Inputs -------------------------------------------------------------


def _build_text_inputs_page(page):
    """TextEntry, PasswordEntry, PathEntry, ScrolledText."""
    bs.Label(
        page, text="Text Inputs", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Specialized entry widgets for text, passwords, and file paths.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # TextEntry
    group = bs.LabelFrame(page, text="TextEntry", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    bs.TextEntry(
        group, label="Name", message="Enter your full name",
    ).pack(fill=X, pady=(0, 8))

    bs.TextEntry(
        group, label="Email", message="example@email.com",
    ).pack(fill=X, pady=(0, 8))

    bs.TextEntry(
        group, label="Disabled", value="Read only", state=DISABLED,
    ).pack(fill=X)

    # PasswordEntry
    group2 = bs.LabelFrame(page, text="PasswordEntry", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.PasswordEntry(
        group2, label="Password", message="Click the eye to toggle visibility",
    ).pack(fill=X)

    # PathEntry
    group3 = bs.LabelFrame(page, text="PathEntry", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    bs.PathEntry(
        group3, label="File", dialog="openfilename",
        message="Select a file to open",
    ).pack(fill=X, pady=(0, 8))

    bs.PathEntry(
        group3, label="Folder", dialog="directory",
        message="Select a directory",
    ).pack(fill=X)

    # ScrolledText
    group4 = bs.LabelFrame(page, text="ScrolledText", padding=15)
    group4.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    text = bs.ScrolledText(group4, height=5, scrollbar_visibility='hover')
    text.pack(fill=BOTH, expand=YES)
    text.insert(END, "ScrolledText provides a multi-line text area with\n")
    text.insert(END, "automatic scrollbars that hide when not needed.\n\n")
    text.insert(END, "Try typing more text to see scrollbars appear!")


# -- Numeric & Date -----------------------------------------------------------


def _build_numeric_page(page):
    """NumericEntry, SpinnerEntry, Scale, LabeledScale, DateEntry, TimeEntry."""
    bs.Label(
        page, text="Numeric & Date", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Numeric entries, sliders, and date/time pickers.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # NumericEntry
    group = bs.LabelFrame(page, text="NumericEntry", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    bs.NumericEntry(
        group, label="Quantity", value=42, minvalue=0, maxvalue=100,
    ).pack(fill=X, pady=(0, 8))

    bs.NumericEntry(
        group, label="Price", value=19.99, increment=0.01,
        value_format="currency",
    ).pack(fill=X)

    # SpinnerEntry
    group2 = bs.LabelFrame(page, text="SpinnerEntry", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.SpinnerEntry(
        group2, label="Month", values=["Jan", "Feb", "Mar", "Apr", "May",
        "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], value="Jan",
    ).pack(fill=X)

    # Scale + LabeledScale
    group3 = bs.LabelFrame(page, text="Scale & LabeledScale", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(group3, text="Scale:").pack(anchor=W)
    bs.Scale(group3, from_=0, to=100, value=50).pack(fill=X, pady=(0, 12))

    bs.Label(group3, text="LabeledScale (with value display):").pack(anchor=W)
    bs.LabeledScale(
        group3, minvalue=0, maxvalue=100, value=65,
    ).pack(fill=X, pady=(0, 4))

    # DateEntry + TimeEntry
    group4 = bs.LabelFrame(page, text="DateEntry & TimeEntry", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    row = bs.Frame(group4)
    row.pack(fill=X, pady=(0, 8))
    bs.DateEntry(row, label="Date").pack(side=LEFT, fill=X, expand=YES, padx=(0, 8))
    bs.TimeEntry(row, label="Time").pack(side=LEFT, fill=X, expand=YES)


# -- Selection ----------------------------------------------------------------


def _build_selection_page(page):
    """CheckButton, Switch, RadioButton, RadioGroup, ToggleGroup, OptionMenu, SelectBox."""
    bs.Label(
        page, text="Selection", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Checkboxes, switches, radio buttons, toggle groups, and option menus.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # CheckButton + Switch
    group = bs.LabelFrame(page, text="CheckButton & Switch", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    row = bs.Frame(group)
    row.pack(fill=X, pady=(0, 10))
    cb1 = bs.CheckButton(row, text="Default", accent="primary")
    cb1.pack(side=LEFT, padx=(0, 12))
    cb1.invoke()
    bs.CheckButton(row, text="Success", accent="success").pack(
        side=LEFT, padx=(0, 12),
    )
    bs.CheckButton(row, text="Disabled", state=DISABLED).pack(side=LEFT)

    row2 = bs.Frame(group)
    row2.pack(fill=X)
    s1 = bs.Switch(row2, text="Notifications", accent="primary")
    s1.pack(side=LEFT, padx=(0, 12))
    s1.invoke()
    bs.Switch(row2, text="Dark Mode", accent="success").pack(
        side=LEFT, padx=(0, 12),
    )
    bs.Switch(row2, text="Disabled", state=DISABLED).pack(side=LEFT)

    # RadioButton + RadioGroup
    group2 = bs.LabelFrame(page, text="RadioButton & RadioGroup", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(group2, text="Individual RadioButtons:").pack(anchor=W, pady=(0, 4))
    row3 = bs.Frame(group2)
    row3.pack(fill=X, pady=(0, 10))
    radio_var = bs.StringVar(value="a")
    for text, val in [("Alpha", "a"), ("Beta", "b"), ("Gamma", "c")]:
        bs.RadioButton(
            row3, text=text, value=val, variable=radio_var,
        ).pack(side=LEFT, padx=(0, 12))

    bs.Label(group2, text="RadioGroup (managed):").pack(anchor=W, pady=(0, 4))
    rg = bs.RadioGroup(group2, value="opt1", accent="primary")
    rg.pack(fill=X)
    rg.add(text="Option 1", value="opt1")
    rg.add(text="Option 2", value="opt2")
    rg.add(text="Option 3", value="opt3")

    # ToggleGroup
    group3 = bs.LabelFrame(page, text="ToggleGroup", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(group3, text="Single select:").pack(anchor=W, pady=(0, 4))
    tg = bs.ToggleGroup(
        group3, mode="single", accent="primary", variant="outline", value="B",
    )
    tg.pack(anchor=W, pady=(0, 10))
    tg.add(text="Bold", value="B")
    tg.add(text="Italic", value="I")
    tg.add(text="Underline", value="U")

    bs.Label(group3, text="Multi select:").pack(anchor=W, pady=(0, 4))
    tg2 = bs.ToggleGroup(
        group3, mode="multi", accent="success", variant="outline",
    )
    tg2.pack(anchor=W)
    tg2.add(text="Python", value="python")
    tg2.add(text="JavaScript", value="javascript")
    tg2.add(text="Rust", value="rust")

    # OptionMenu + SelectBox
    group4 = bs.LabelFrame(page, text="OptionMenu & SelectBox", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    row4 = bs.Frame(group4)
    row4.pack(fill=X, pady=(0, 8))
    bs.Label(row4, text="OptionMenu:", width=12).pack(side=LEFT)
    bs.OptionMenu(
        row4, value="Red",
        options=["Red", "Green", "Blue", "Yellow"],
    ).pack(side=LEFT)

    bs.SelectBox(
        group4, label="SelectBox:",
        items=["Small", "Medium", "Large", "Extra Large"],
        value="Medium",
    ).pack(fill=X)


# -- Calendar -----------------------------------------------------------------


def _build_calendar_page(page):
    """Calendar widget demonstration."""
    bs.Label(
        page, text="Calendar", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Interactive date picker with single and range selection modes.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    group = bs.LabelFrame(page, text="Single Selection", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    bs.Calendar(group, accent="primary").pack()

    group2 = bs.LabelFrame(page, text="Range Selection", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.Calendar(
        group2, selection_mode="range", accent="success",
    ).pack()


# -- Forms --------------------------------------------------------------------


def _build_forms_page(page):
    """Form widget with various editor types and grouping."""
    bs.Label(
        page, text="Forms", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Spec-driven form builder for consistent data-entry UIs.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Inferred form (from data)
    bs.Label(page, text="Inferred Form", font="body[bold]").pack(anchor=W, padx=20, pady=(0, 4))

    form1 = bs.Form(
        page,
        data={
            "first_name": "Jane",
            "last_name": "Doe",
            "age": 34,
            "email": "jane@example.com",
            "salary": 120000.50,
            "active": True,
        },
        col_count=2,
        min_col_width=220,
    )
    form1.pack(fill=X, padx=20)

    # Explicit form with groups
    bs.Label(page, text="Explicit Form Layout", font="body[bold]").pack(anchor=W, padx=20, pady=(16, 4))

    form2 = bs.Form(
        page,
        data={"username": "jdoe", "role": "Admin", "newsletter": True, "timezone": "UTC"},
        items=[
            {
                "type": "group",
                "label": "Profile",
                "col_count": 2,
                "items": [
                    {"key": "username", "label": "Username"},
                    {"key": "password", "label": "Password", "editor": "passwordentry"},
                    {"key": "role", "label": "Role", "editor": "selectbox", "items": ["Admin", "User", "Viewer"]},
                ],
            },
            {
                "type": "group",
                "label": "Preferences",
                "items": [
                    {"key": "newsletter", "label": "Newsletter", "editor": "switch"},
                    {"key": "timezone", "label": "Time Zone", "editor": "selectbox", "items": ["UTC", "US/Eastern", "US/Central", "US/Pacific"]},
                ],
            },
        ],
    )
    form2.pack(fill=X, padx=20, pady=(0, 15))


# -- Data Display -------------------------------------------------------------


def _build_data_page(page):
    """Label, Badge, TreeView, TableView."""
    bs.Label(
        page, text="Data Display", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Labels, badges, trees, and tables for presenting data.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Labels with accents
    group = bs.LabelFrame(page, text="Labels", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    row = bs.Frame(group)
    row.pack(fill=X)
    for color in ("primary", "secondary", "success", "info", "warning", "danger"):
        bs.Label(
            row, text=color.title(), accent=color, padding=(8, 4),
        ).pack(side=LEFT, padx=2)

    # Badges
    group2 = bs.LabelFrame(page, text="Badges", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    row2 = bs.Frame(group2)
    row2.pack(fill=X)
    for color in ("primary", "success", "warning", "danger", "info"):
        bs.Badge(
            row2, text=color.title(), accent=color,
        ).pack(side=LEFT, padx=4)

    row3 = bs.Frame(group2)
    row3.pack(fill=X, pady=(8, 0))
    bs.Badge(row3, text="Pill", accent="primary", variant="pill").pack(
        side=LEFT, padx=4,
    )
    bs.Badge(row3, text="99+", accent="danger", variant="pill").pack(
        side=LEFT, padx=4,
    )
    bs.Badge(row3, text="New", accent="success").pack(side=LEFT, padx=4)

    # TreeView
    group3 = bs.LabelFrame(page, text="TreeView", padding=15)
    group3.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    columns = ("name", "status", "progress")
    tree = bs.TreeView(group3, columns=columns, show="headings", height=5)

    tree.heading("name", text="Task Name")
    tree.heading("status", text="Status")
    tree.heading("progress", text="Progress")

    tree.column("name", width=200)
    tree.column("status", width=100, anchor=CENTER)
    tree.column("progress", width=100, anchor=CENTER)

    for item in [
        ("Database Migration", "Complete", "100%"),
        ("API Integration", "In Progress", "65%"),
        ("UI Redesign", "In Progress", "40%"),
        ("Testing Suite", "Pending", "0%"),
        ("Documentation", "In Progress", "80%"),
    ]:
        tree.insert("", END, values=item)

    tree.pack(fill=BOTH, expand=YES)
    tree.selection_set(tree.get_children()[0])

    # TableView
    group4 = bs.LabelFrame(page, text="TableView", padding=15, height=300)
    group4.pack(fill=X, padx=20, pady=(0, 10))
    group4.pack_propagate(False)

    tv = bs.TableView(
        group4,
        columns=[
            {"text": "Name", "stretch": True},
            {"text": "Department", "width": 120},
            {"text": "Salary", "width": 100, "anchor": "e"},
        ],
        rows=[
            ("Alice Johnson", "Engineering", "$120,000"),
            ("Bob Smith", "Marketing", "$85,000"),
            ("Carol White", "Engineering", "$115,000"),
            ("David Brown", "Design", "$95,000"),
            ("Eve Davis", "Marketing", "$88,000"),
        ],
    )
    tv.pack(fill=BOTH, expand=YES)


# -- Progress & Meters --------------------------------------------------------


def _build_progress_page(page):
    """Progressbar, Meter, FloodGauge, Scale (interactive)."""
    bs.Label(
        page, text="Progress & Meters", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Progress bars, meters, and gauges for showing values and status.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    slider_value = Signal[float](65.0)

    # Scale driving progress bars
    group = bs.LabelFrame(
        page, text="Scale (drag to control progress bars)", padding=15,
    )
    group.pack(fill=X, padx=20, pady=(0, 10))

    bs.Scale(group, from_=0, to=100, signal=slider_value).pack(fill=X)

    # Progressbar
    group2 = bs.LabelFrame(page, text="Progressbar", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.Progressbar(group2, signal=slider_value, maximum=100).pack(
        fill=X, pady=(0, 8),
    )
    bs.Progressbar(
        group2, value=75, maximum=100, accent="success", variant="striped",
    ).pack(fill=X, pady=(0, 8))
    bs.Progressbar(
        group2, value=45, maximum=100, accent="danger",
    ).pack(fill=X, pady=(0, 8))
    bs.Progressbar(
        group2, value=30, maximum=100, accent="warning", variant="thin",
    ).pack(fill=X)

    # Meters
    group3 = bs.LabelFrame(page, text="Meter", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    meter_row = bs.Frame(group3)
    meter_row.pack()

    for amount, label, color in [
        (45, "CPU Usage", "info"),
        (78, "Memory", "warning"),
        (92, "Disk", "danger"),
    ]:
        bs.Meter(
            meter_row,
            metersize=120,
            amountused=amount,
            amounttotal=100,
            subtext=label,
            accent=color,
            interactive=True,
        ).pack(side=LEFT, padx=10)

    # FloodGauge
    # Note: FloodGauge has a known issue with theme changes, so we
    # guard against errors during the demo.
    group4 = bs.LabelFrame(page, text="FloodGauge", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    fg_row = bs.Frame(group4)
    fg_row.pack(fill=X)

    for val, color, mask in [
        (65, "primary", "{}%"),
        (82, "success", "{}% Done"),
        (35, "danger", "{}% Used"),
    ]:
        bs.FloodGauge(
            fg_row, value=val, maximum=100, accent=color,
            mask=mask, length=150, thickness=40,
        ).pack(side=LEFT, padx=4, expand=YES)


# -- Layout -------------------------------------------------------------------


def _build_layout_page(page):
    """Card, LabelFrame, Expander, Accordion, PanedWindow, Separator."""
    bs.Label(
        page, text="Layout", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Containers, expandable panels, and split panes for organizing content.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # Card
    group = bs.LabelFrame(page, text="Card", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    card_row = bs.Frame(group)
    card_row.pack(fill=X)

    for title, body, color in [
        ("Users", "1,234 active", "primary"),
        ("Revenue", "$45,678", "success"),
        ("Errors", "12 today", "danger"),
    ]:
        card = bs.Card(card_row, padding=16)
        card.pack(side=LEFT, padx=4, expand=YES, fill=X)
        bs.Label(card, text=title, accent=color, font="body[bold]").pack(anchor=W)
        bs.Label(card, text=body, font="heading-lg").pack(anchor=W)

    # Expander
    group2 = bs.LabelFrame(page, text="Expander", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    exp = bs.Expander(group2, title="Click to expand", expanded=False)
    exp.pack(fill=X, pady=(0, 8))
    bs.Label(
        exp.content, text="This content is revealed when the expander is opened.",
        padding=10,
    ).pack(fill=X)

    exp2 = bs.Expander(group2, title="Already expanded", expanded=True)
    exp2.pack(fill=X)
    bs.Label(
        exp2.content, text="Expanders can start open or closed.",
        padding=10,
    ).pack(fill=X)

    # Accordion
    group3 = bs.LabelFrame(page, text="Accordion", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    acc = bs.Accordion(group3)
    acc.pack(fill=X)

    sec1 = acc.add(title="Section 1")
    bs.Label(sec1.content, text="Content for section one.", padding=10).pack(fill=X)

    sec2 = acc.add(title="Section 2")
    bs.Label(sec2.content, text="Content for section two.", padding=10).pack(fill=X)

    sec3 = acc.add(title="Section 3")
    bs.Label(sec3.content, text="Content for section three.", padding=10).pack(fill=X)

    # PanedWindow
    group4 = bs.LabelFrame(page, text="PanedWindow", padding=15)
    group4.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    pw = bs.PanedWindow(group4, orient=HORIZONTAL)
    pw.pack(fill=BOTH, expand=YES)

    left = bs.LabelFrame(pw, text="Left Pane", padding=10)
    bs.Label(left, text="Drag the\nsash to resize", justify=CENTER).pack(expand=YES)
    pw.add(left, weight=1)

    right = bs.LabelFrame(pw, text="Right Pane", padding=10)
    bs.Label(right, text="Both panes\nare resizable", justify=CENTER).pack(expand=YES)
    pw.add(right, weight=1)

    # Separator
    group5 = bs.LabelFrame(page, text="Separator", padding=15)
    group5.pack(fill=X, padx=20, pady=(0, 10))

    bs.Separator(group5).pack(fill=X, pady=(0, 8))
    bs.Separator(group5, accent="primary").pack(fill=X, pady=(0, 8))
    bs.Separator(group5, accent="success").pack(fill=X, pady=(0, 8))
    bs.Separator(group5, accent="danger").pack(fill=X)


# -- Navigation ---------------------------------------------------------------


def _build_navigation_page(page):
    """TabView and Notebook demonstrations."""
    bs.Label(
        page, text="Navigation", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Tab-based navigation widgets for organizing content into views.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # TabView
    group = bs.LabelFrame(page, text="TabView (bar variant)", padding=15)
    group.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    tv = TabView(group, variant="bar")
    tv.pack(fill=BOTH, expand=YES)

    tab1 = tv.add("dashboard", text="Dashboard")
    bs.Label(tab1, text="Dashboard content goes here.", padding=20).pack(expand=YES)

    tab2 = tv.add("analytics", text="Analytics")
    bs.Label(tab2, text="Analytics content goes here.", padding=20).pack(expand=YES)

    tab3 = tv.add("settings", text="Settings")
    bs.Label(tab3, text="Settings content goes here.", padding=20).pack(expand=YES)

    # TabView with accent
    group2 = bs.LabelFrame(page, text="TabView (with accent)", padding=15)
    group2.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    tv2 = TabView(group2, variant="bar", accent="success")
    tv2.pack(fill=BOTH, expand=YES)

    p1 = tv2.add("all", text="All")
    bs.Label(p1, text="Showing all items.", padding=20).pack(expand=YES)

    p2 = tv2.add("active", text="Active")
    bs.Label(p2, text="Showing active items.", padding=20).pack(expand=YES)

    p3 = tv2.add("archived", text="Archived")
    bs.Label(p3, text="Showing archived items.", padding=20).pack(expand=YES)

    # Notebook
    group3 = bs.LabelFrame(page, text="Notebook (classic tabs)", padding=15)
    group3.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 10))

    nb = bs.Notebook(group3)
    nb.pack(fill=BOTH, expand=YES)

    for label in ("General", "Advanced", "About"):
        f = bs.Frame(nb, padding=15)
        nb.add(f, text=label)
        bs.Label(f, text=f"{label} tab content.").pack(expand=YES)


# -- Overlays ----------------------------------------------------------------


def _build_overlays_page(page):
    """Toast and ToolTip demonstrations."""
    bs.Label(
        page, text="Overlays", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Toasts, tooltips, and other overlay widgets.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # ToolTip
    group = bs.LabelFrame(page, text="ToolTip", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(
        group, text="Hover over the buttons below to see tooltips:",
    ).pack(anchor=W, pady=(0, 8))

    row = bs.Frame(group)
    row.pack(fill=X)

    btn1 = bs.Button(row, text="Default Tooltip", accent="primary")
    btn1.pack(side=LEFT, padx=(0, 8))
    bs.ToolTip(btn1, text="This is a basic tooltip.")

    btn2 = bs.Button(row, text="Info Tooltip", accent="info")
    btn2.pack(side=LEFT, padx=(0, 8))
    bs.ToolTip(btn2, text="Tooltips can have accent colors.", accent="info")

    btn3 = bs.Button(row, text="Long Tooltip", accent="secondary")
    btn3.pack(side=LEFT)
    bs.ToolTip(
        btn3,
        text="This is a longer tooltip that wraps text. It shows how "
        "tooltips handle multi-line content with wraplength.",
        wraplength=200,
    )

    # Toast
    group2 = bs.LabelFrame(page, text="Toast", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(
        group2, text="Click buttons to show toast notifications:",
    ).pack(anchor=W, pady=(0, 8))

    row2 = bs.Frame(group2)
    row2.pack(fill=X)

    def show_toast(title, message, accent):
        bs.Toast(
            title=title,
            message=message,
            accent=accent,
            duration=3000,
        ).show()

    bs.Button(
        row2, text="Success Toast", accent="success",
        command=lambda: show_toast("Success", "Operation completed.", "success"),
    ).pack(side=LEFT, padx=(0, 8))

    bs.Button(
        row2, text="Warning Toast", accent="warning",
        command=lambda: show_toast("Warning", "Check your settings.", "warning"),
    ).pack(side=LEFT, padx=(0, 8))

    bs.Button(
        row2, text="Error Toast", accent="danger",
        command=lambda: show_toast("Error", "Something went wrong.", "danger"),
    ).pack(side=LEFT)


# -- Dialogs ------------------------------------------------------------------


def _build_dialogs_page(page):
    """Dialog demonstrations — each button launches a dialog."""
    bs.Label(
        page, text="Dialogs", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Click buttons to launch various dialog types.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    # MessageBox / MessageDialog
    group1 = bs.LabelFrame(page, text="MessageBox & MessageDialog", padding=15)
    group1.pack(fill=X, padx=20, pady=(0, 10))

    row1 = bs.Frame(group1)
    row1.pack(fill=X)

    def show_message_ok():
        bs.MessageBox.ok("This is an informational message.", title="Info")

    def show_message_yesno():
        result = bs.MessageBox.yesno("Do you want to continue?", title="Confirm")
        bs.Toast(title="Result", message=f"You chose: {result}", duration=2000).show()

    def show_message_okcancel():
        result = bs.MessageBox.okcancel("Save changes before closing?", title="Save")
        bs.Toast(title="Result", message=f"You chose: {result}", duration=2000).show()

    bs.Button(row1, text="Info (OK)", command=show_message_ok).pack(side=LEFT, padx=(0, 8))
    bs.Button(row1, text="Yes / No", command=show_message_yesno).pack(side=LEFT, padx=(0, 8))
    bs.Button(row1, text="OK / Cancel", command=show_message_okcancel).pack(side=LEFT)

    # QueryBox
    group2 = bs.LabelFrame(page, text="QueryBox", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    row2 = bs.Frame(group2)
    row2.pack(fill=X)

    def show_query_string():
        result = bs.QueryBox.get_string("Enter your name:", title="String Input")
        if result is not None:
            bs.Toast(title="Input", message=f"You entered: {result}", duration=2000).show()

    def show_query_integer():
        result = bs.QueryBox.get_integer("Enter a number:", title="Integer Input", minvalue=0, maxvalue=100)
        if result is not None:
            bs.Toast(title="Input", message=f"You entered: {result}", duration=2000).show()

    bs.Button(row2, text="Get String", command=show_query_string).pack(side=LEFT, padx=(0, 8))
    bs.Button(row2, text="Get Integer", command=show_query_integer).pack(side=LEFT)

    # ColorChooser
    group3 = bs.LabelFrame(page, text="ColorChooser", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    color_swatch = bs.Label(group3, text="  Selected Color  ", padding=8, surface="card")
    color_swatch.pack(side=LEFT, padx=(0, 12))

    def show_color_chooser():
        result = bs.ColorChooserDialog().show()
        if result:
            bs.Toast(title="Color", message=f"Selected: {result}", duration=2000).show()

    bs.Button(group3, text="Choose Color", command=show_color_chooser).pack(side=LEFT)

    # FontDialog
    group4 = bs.LabelFrame(page, text="FontDialog", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    def show_font_dialog():
        result = bs.FontDialog().show()
        if result:
            bs.Toast(title="Font", message=f"Selected: {result}", duration=2000).show()

    bs.Button(group4, text="Choose Font", command=show_font_dialog).pack(side=LEFT)

    # DateDialog
    group5 = bs.LabelFrame(page, text="DateDialog", padding=15)
    group5.pack(fill=X, padx=20, pady=(0, 10))

    def show_date_dialog():
        result = bs.DateDialog().show()
        if result:
            bs.Toast(title="Date", message=f"Selected: {result}", duration=2000).show()

    bs.Button(group5, text="Pick Date", command=show_date_dialog).pack(side=LEFT)


# -- Themes -------------------------------------------------------------------


def _build_theme_page(page):
    """Theme settings page."""
    bs.Label(
        page, text="Themes", font="heading-xl",
    ).pack(anchor=W, padx=20, pady=(20, 10))

    bs.Label(
        page,
        text="Switch themes to see all widgets update in real time.",
        accent="secondary",
    ).pack(anchor=W, padx=20, pady=(0, 15))

    group = bs.LabelFrame(page, text="Theme Selector", padding=15)
    group.pack(fill=X, padx=20, pady=(0, 10))

    style = bs.get_style()
    theme_names = sorted(
        s["name"] for s in style.theme_provider.list_themes()
    )

    row = bs.Frame(group)
    row.pack(fill=X, pady=(0, 10))
    bs.Label(row, text="Theme:", width=12).pack(side=LEFT)

    combo = bs.Combobox(row, values=theme_names, width=20, state="readonly")
    combo.pack(side=LEFT)
    combo.set(style.current_theme)

    def on_change(event):
        style.theme_use(combo.get())
        combo.selection_clear()

    combo.bind("<<ComboboxSelected>>", on_change)

    # Quick toggle
    row2 = bs.Frame(group)
    row2.pack(fill=X)
    bs.Label(row2, text="Quick:", width=12).pack(side=LEFT)
    bs.Button(
        row2, text="Toggle Light / Dark", command=bs.toggle_theme,
    ).pack(side=LEFT)

    # Semantic accent colors
    group2 = bs.LabelFrame(page, text="Semantic Colors", padding=15)
    group2.pack(fill=X, padx=20, pady=(0, 10))

    accent_row = bs.Frame(group2)
    accent_row.pack(fill=X, pady=(0, 10))
    for color in ("primary", "secondary", "success", "info", "warning", "danger"):
        bs.Button(accent_row, text=color.title(), accent=color).pack(side=LEFT, padx=4, expand=YES, fill=X)

    extra_row = bs.Frame(group2)
    extra_row.pack(fill=X)
    for color in ("light", "dark"):
        bs.Button(extra_row, text=color.title(), accent=color).pack(side=LEFT, padx=4, expand=YES, fill=X)

    # Surface colors
    group3 = bs.LabelFrame(page, text="Surfaces", padding=15)
    group3.pack(fill=X, padx=20, pady=(0, 10))

    surface_row = bs.Frame(group3)
    surface_row.pack(fill=X)
    for surface in ("chrome", "content", "card", "overlay", "input"):
        f = bs.Frame(surface_row, surface=surface, padding=12)
        f.pack(side=LEFT, padx=4, expand=YES, fill=X)
        bs.Label(f, text=surface.title(), surface=surface).pack()

    # Stroke / border colors
    group4 = bs.LabelFrame(page, text="Borders & Strokes", padding=15)
    group4.pack(fill=X, padx=20, pady=(0, 10))

    bs.Label(group4, text="stroke").pack(anchor=W)
    bs.Separator(group4).pack(fill=X, pady=(2, 8))
    bs.Label(group4, text="stroke_subtle").pack(anchor=W)
    bs.Separator(group4, accent="stroke_subtle").pack(fill=X, pady=(2, 0))


# =============================================================================
# Gallery app
# =============================================================================


def run_demo():
    """Run the bootstack widget gallery as an AppShell application."""
    shell = bs.AppShell(
        title="Widget Gallery",
        theme="bootstrap-light",
        size=(1100, 750),
    )

    # Toolbar: theme toggle
    shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)

    # Page definitions: (key, text, icon, builder, scrollable, extra_kwargs)
    pages = [
        # Home
        ("home", "Home", "house", _build_home_page, False, {}),
        # Actions
        ("buttons", "Buttons", "hand-index-thumb", _build_buttons_page, True, {}),
        # Inputs
        ("text-inputs", "Text Inputs", "input-cursor-text", _build_text_inputs_page, True, {}),
        ("numeric", "Numeric Date", "123", _build_numeric_page, True, {}),
        ("forms", "Forms", "journal-text", _build_forms_page, True, {}),
        # Selection
        ("selection", "Selection", "ui-checks", _build_selection_page, True, {}),
        ("calendar", "Calendar", "calendar3", _build_calendar_page, True, {}),
        # Data Display
        ("data", "Data Tables", "table", _build_data_page, True, {}),
        ("progress", "Progress", "speedometer2", _build_progress_page, True, {}),
        # Layout
        ("layout", "Containers", "layout-wtf", _build_layout_page, True, {}),
        # Navigation
        ("navigation", "Tabs Views", "window-stack", _build_navigation_page, True, {}),
        # Overlays
        ("overlays", "Overlays", "layers", _build_overlays_page, True, {}),
        # Dialogs
        ("dialogs", "Dialogs", "chat-square-text", _build_dialogs_page, True, {}),
        # Design System
        ("themes", "Themes", "palette", _build_theme_page, True, {}),
        ("typography", "Typography", "fonts", _build_typography_page, True, {}),
        ("icons", "Icons", "grid-3x3-gap", _build_icons_page, True, {}),
    ]

    # Sidebar structure (headers and separators between groups)
    sidebar_structure = {
        "buttons": ("separator", "Actions"),
        "text-inputs": ("separator", "Inputs"),
        "selection": ("separator", "Selection"),
        "data": ("separator", "Data Display"),
        "layout": ("separator", "Layout"),
        "themes": ("separator", "Design System"),
    }

    # Register all pages (lightweight — no widget building yet)
    _builders = {}  # key -> (builder, page_widget)

    for key, text, icon, builder, scrollable, kwargs in pages:
        # Insert sidebar headers/separators before certain pages
        if key in sidebar_structure:
            shell.add_separator()
            shell.add_header(sidebar_structure[key][1])

        page = shell.add_page(key, text=text, icon=icon, scrollable=scrollable, **kwargs)
        _builders[key] = (builder, page)

    # Build only the home page eagerly
    _built = set()
    _build_home_page(_builders["home"][1])
    _built.add("home")

    # Lazy-build pages on first navigation via PageStack hook
    _orig_ps_navigate = shell.pages.navigate

    def _lazy_ps_navigate(key, data=None, **kwargs):
        if key not in _built and key in _builders:
            builder, page = _builders[key]
            builder(page)
            _built.add(key)
        return _orig_ps_navigate(key, data=data, **kwargs)

    shell.pages.navigate = _lazy_ps_navigate

    shell.navigate("home")
    shell.mainloop()


def setup_demo(master):
    """Setup the demo widgets - legacy compatibility.

    Note: The gallery now uses AppShell, so this legacy entry point
    creates a simplified widget showcase in the given master frame.
    """
    from bootstack.constants import BOTH, YES

    bs.Label(
        master,
        text="Use 'bootstack gallery' to launch the Widget Gallery.",
        font="heading-lg",
        padding=40,
    ).pack(fill=BOTH, expand=YES)
