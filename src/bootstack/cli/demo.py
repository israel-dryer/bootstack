"""
Widget Gallery

A hero-first showcase of bootstack widgets, organized by category. Each sidebar
page shows one representative instance of each widget — variants and colors only
where they're meaningful (accent palettes, key modes) rather than an exhaustive
matrix. Kept deliberately lean.
"""

import bootstack as bs
from bootstack.signals import Signal
from bootstack.dialogs import FormDialog
from bootstack.style.style import get_style


# =============================================================================
# Page builders — one hero page per category
# =============================================================================


def _heading(title, subtitle):
    bs.Label(title, font="heading-xl")
    bs.Label(subtitle, accent="secondary")


def _build_home_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        bs.Label("bootstack", font="display-lg[bold]")
        bs.Label("A batteries-included desktop UI framework for Python.",
                 font="body-lg", accent="secondary")

        with bs.Row(gap=16, grow_items=True):
            for title, body, icon, color in [
                ("Widgets", "50+ composable widgets", "grid-3x3-gap", "primary"),
                ("Theming", "Live light/dark themes", "palette", "success"),
                ("Data", "Tables, trees, sources", "table", "info"),
            ]:
                with bs.Card(accent=color, gap=6):
                    bs.Label(title, icon=icon, accent=color, font="body[bold]")
                    bs.Label(body, accent="secondary", font="caption")

        with bs.GroupBox("About this gallery"):
            bs.Label(
                "Browse the sidebar to explore widgets by category. Each page shows "
                "a representative example — switch the theme from the toolbar to see "
                "everything update live."
            )


def _build_actions_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Actions", "Buttons and action triggers.")

        with bs.GroupBox("Button — accents", grow_items=True, gap=4, layout="row"):
            for color in ("default", "primary", "success", "warning", "danger"):
                bs.Button(color.title(), accent=color)

        with bs.GroupBox("Button — variants", layout="row", gap=4, grow_items=True):
            for variant in ("solid", "outline", "ghost"):
                bs.Button(variant.title(), accent="primary", variant=variant)
            bs.Button("Disabled", accent="primary", disabled=True)

        with bs.GroupBox("ButtonGroup, MenuButton", layout="row", gap=16):
            bg = bs.ButtonGroup(accent="primary", variant="outline")
            bg.add("Cut", icon="scissors")
            bg.add("Copy", icon="copy")
            bg.add("Paste", icon="clipboard")

            mb = bs.MenuButton("Actions", icon="three-dots", accent="primary")
            mb.add_item("New file", icon="file-earmark")
            mb.add_item("Open…", icon="folder2-open")
            mb.add_divider()
            mb.add_item("Delete", icon="trash")

        with bs.GroupBox("ThemeToggle", layout="row", gap=8, vertical_items="center"):
            bs.Label("Light / dark switch:")
            bs.ThemeToggle()


def _build_inputs_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Inputs", "Text, numeric, path, and date/time entry fields.")

        with bs.GroupBox("Text", horizontal_items="stretch", gap=6):
            bs.TextField(label="Name", message="Enter your full name")
            bs.PasswordField(label="Password", message="Click the eye to reveal")
            bs.PathField(label="File", mode="open", message="Select a file")

        with bs.GroupBox("Numeric", gap=8, layout="row", grow_items=True):
            bs.NumberField(label="Quantity", value=42, min_value=0, max_value=100)
            bs.SpinnerField(
                label="Month",
                options=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                value="Jan",
            )

        with bs.GroupBox("Date & time", gap=8, layout="row", grow_items=True):
            bs.DateField(label="Date")
            bs.TimeField(label="Time")

        with bs.GroupBox("Sliders", horizontal_items="stretch", gap=12):
            bs.Slider(value=65, show_value=True, tick_step=25)
            bs.RangeSlider(low_value=25, high_value=75, min_value=0, max_value=100,
                           show_value=True, accent="primary")


_DEMO_PYTHON = '''\
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("bootstack"))
'''

_DEMO_JSON = '''\
{
    "name": "bootstack",
    "version": "1.0.0",
    "description": "Modern UI framework for Python"
}
'''


def _build_editing_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Text editing", "Multi-line text and a syntax-highlighting editor.")

        with bs.GroupBox("TextArea", horizontal_items="stretch"):
            bs.TextArea(
                value="Multi-line input with scrollbars, undo/redo, and signal "
                      "binding.\n\nTry typing more to see it scroll.",
                height=5,
                grow=True,
            )

        with bs.GroupBox("CodeEditor — Python", horizontal_items="stretch", gap=6):
            editor = bs.CodeEditor(_DEMO_PYTHON, language="python", height=10)
            with bs.Row(gap=6, vertical_items="center"):
                bs.Button("Undo", variant="outline", on_click=editor.undo)
                bs.Button("Redo", variant="outline", on_click=editor.redo)
                bs.Button("Find", variant="outline", icon="search",
                          on_click=editor.show_search)

        with bs.GroupBox("CodeEditor — JSON (read-only)", horizontal_items="stretch"):
            bs.CodeEditor(_DEMO_JSON, language="json", read_only=True, height=6)


def _build_selection_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Selection", "Checkboxes, switches, radios, toggles, and pickers.")

        with bs.GroupBox("Checkbox & Switch", gap=8, layout="row"):
            bs.Checkbox("Enabled", accent="primary", value=True)
            bs.Switch("Notifications", accent="success", value=True)

        with bs.GroupBox("RadioGroup, ToggleGroup", gap=16, layout="row"):
            rg = bs.RadioGroup(value="opt1", accent="primary")
            rg.add("Option 1", value="opt1")
            rg.add("Option 2", value="opt2")
            rg.add("Option 3", value="opt3")

            with bs.Column(gap=4):
                bs.Label("Multi-select:", font="caption", accent="secondary")
                tg = bs.ToggleGroup(mode="multi", accent="success", variant="outline")
                tg.add("Bold", value="B")
                tg.add("Italic", value="I")
                tg.add("Underline", value="U")

        with bs.GroupBox("Select & SelectButton", horizontal_items="stretch", gap=8):
            bs.Select(label="Size", options=["Small", "Medium", "Large"], value="Medium")
            bs.SelectButton(options=["Day", "Week", "Month"], value="Week", accent="primary")

        with bs.GroupBox("Calendar", layout="row", gap=16):
            bs.Calendar(accent="primary")


def _build_data_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Data display", "Labels, badges, progress bars, and gauges.")

        with bs.GroupBox("Badges — accents", gap=12, layout="row"):
            for color in ("primary", "success", "warning", "danger"):
                bs.Badge(color.title(), accent=color)
            bs.Badge("99+", accent="danger", variant="pill")

        with bs.GroupBox("ProgressBar", horizontal_items="stretch", gap=8):
            bs.ProgressBar(value=70, max_value=100, accent="primary")
            bs.ProgressBar(value=45, max_value=100, accent="success")

        with bs.GroupBox("Gauge", layout="row", gap=16, vertical_items="center"):
            for amount, label, color in [
                (45, "CPU", "primary"),
                (78, "Memory", "warning"),
                (92, "Disk", "danger"),
            ]:
                bs.Gauge(value=amount, max_value=100, subtitle=label,
                         accent=color, interactive=True)


def _build_tables_page():
    employees = [
        {"name": "Ada Lovelace", "role": "Staff Engineer", "dept": "Engineering", "salary": 185000},
        {"name": "Alan Turing", "role": "Software Engineer", "dept": "Engineering", "salary": 162000},
        {"name": "Grace Hopper", "role": "Engineering Lead", "dept": "Engineering", "salary": 198000},
        {"name": "Carol Williams", "role": "Product Designer", "dept": "Design", "salary": 142000},
        {"name": "Eva Martinez", "role": "Account Executive", "dept": "Sales", "salary": 129000},
        {"name": "Iris Chen", "role": "Content Strategist", "dept": "Marketing", "salary": 112000},
    ]

    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Data tables", "List, table, and tree views over records.")

        with bs.GroupBox("ListView"):
            bs.ListView(
                items=[
                    {"id": 1, "title": "Inbox", "text": "12 unread", "icon": "inbox", "badge": "12"},
                    {"id": 2, "title": "Starred", "text": "Flagged items", "icon": "star-fill"},
                    {"id": 3, "title": "Sent", "text": "Your sent mail", "icon": "send"},
                ],
                selection_mode="single",
                height=150,
            )

        with bs.GroupBox("DataTable", horizontal_items="stretch", grow=True):
            bs.DataTable(
                columns=[
                    {"text": "Name", "key": "name", "width": 200},
                    {"text": "Role", "key": "role", "width": 180},
                    {"text": "Department", "key": "dept", "width": 140},
                    {"text": "Salary", "key": "salary", "width": 120, "anchor": "e", "format": "${:,.0f}"},
                ],
                rows=employees,
                selection_mode="multi",
                show_selection_controls=True,
                allow_filter=True,
                allow_group=True,
                grow=True,
            )

        with bs.GroupBox("Tree"):
            bs.Tree(
                nodes=[
                    {"label": "Engineering", "open_icon": "folder2-open",
                     "closed_icon": "folder-fill", "expanded": True, "children": [
                         {"label": "Ada Lovelace", "icon": "person-fill"},
                         {"label": "Grace Hopper", "icon": "person-fill"},
                     ]},
                    {"label": "Design", "open_icon": "folder2-open",
                     "closed_icon": "folder-fill", "children": [
                         {"label": "Carol Williams", "icon": "person-fill"},
                     ]},
                ],
                height=200,
            )


def _demo_photos():
    """A few solid-color tiles as `Image` handles, for the media widgets."""
    from PIL import Image as _PILImage
    from bootstack.images import Image

    swatches = [
        ("Sunset", (244, 114, 82)), ("Ocean", (56, 132, 222)),
        ("Forest", (71, 159, 118)), ("Berry", (176, 42, 88)),
        ("Amber", (240, 180, 41)), ("Slate", (90, 99, 110)),
    ]
    return [
        {"title": name, "image": Image.from_pil(_PILImage.new("RGB", (320, 320), rgb))}
        for name, rgb in swatches
    ]


def _build_media_page():
    from bootstack.images import get_icon

    photos = _demo_photos()

    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Media", "Avatars, images, carousels, and thumbnail grids.")

        with bs.GroupBox("Avatar", layout="row", gap=12):
            bs.Avatar(name="Ada Lovelace")
            bs.Avatar(name="Grace Hopper", shape="rounded")
            bs.Avatar(initials="JS", shape="square")
            bs.Avatar(image=get_icon("person-fill", size=40))

        with bs.GroupBox("Picture", layout="row", gap=16):
            bs.Picture(photos[0]["image"], width=180, height=120, fit="cover", corner_radius=8)
            bs.Picture(photos[1]["image"], width=120, height=120, fit="cover", corner_radius=60)

        with bs.GroupBox("Carousel", horizontal_items="stretch"):
            bs.Carousel(items=photos, image_field="image", caption_field="title", fit="cover")

        with bs.GroupBox("Gallery", horizontal_items="stretch", grow=True):
            bs.Gallery(items=photos, image_field="image", caption_field="title",
                       tile_size=(120, 120), grow=True)


def _build_layout_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Layout", "Cards, panels, dividers, and split panes.")

        with bs.GroupBox("Card", layout="row", grow_items=True, gap=16):
            for title, body, color in [
                ("Users", "1,234 active", "primary"),
                ("Revenue", "$45,678", "success"),
                ("Errors", "12 today", "danger"),
            ]:
                with bs.Card(accent=color):
                    bs.Label(title, accent=color, font="body[bold]")
                    bs.Label(body, font="heading-lg")

        with bs.GroupBox("Accordion"):
            acc = bs.Accordion(accent="primary")
            with acc.add("Section 1", expanded=True):
                bs.Label("Content for section one.")
            with acc.add("Section 2"):
                bs.Label("Content for section two.")

        with bs.GroupBox("SplitView", horizontal_items="stretch", grow=True):
            sv = bs.SplitView(orient="horizontal", grow=True)
            with sv.add(padding=10, horizontal_items="center"):
                bs.Label("Left pane")
                bs.Label("Drag the sash to resize", accent="secondary", font="caption")
            with sv.add(padding=10, horizontal_items="center"):
                bs.Label("Right pane")

        with bs.GroupBox("ScrollView", horizontal_items="stretch"):
            with bs.ScrollView(height=120, show_border=True, padding=8):
                for i in range(20):
                    bs.Label(f"Scrollable row {i + 1}")

        with bs.GroupBox("Divider — accents", horizontal_items="stretch", gap=8):
            bs.Divider()
            bs.Divider(accent="primary")


def _build_navigation_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Navigation & overlays", "Tabs, page stacks, tooltips, toasts, menus.")

        with bs.GroupBox("Tabs", horizontal_items="stretch", grow=True):
            tabs = bs.Tabs(grow=True)
            with tabs.add("dashboard", label="Dashboard", icon="house"):
                bs.Label("Dashboard content.", padding=20)
            with tabs.add("files", label="Files", icon="folder2"):
                bs.Label("Browse your files.", padding=20)
            with tabs.add("settings", label="Settings", icon="gear"):
                bs.Label("Configure settings.", padding=20)

        with bs.GroupBox("PageStack", horizontal_items="stretch", grow=True):
            ps = bs.PageStack(grow=True)
            with ps.add("welcome"):
                bs.Label("Welcome page", font="heading-md", padding=20)
            with ps.add("details"):
                bs.Label("Details page", font="heading-md", padding=20)
            with bs.Row(gap=8):
                bs.Button("Welcome", on_click=lambda: ps.navigate("welcome"))
                bs.Button("Details", on_click=lambda: ps.navigate("details"))

        with bs.GroupBox("Tooltip & Toast", layout="row", gap=8):
            tip = bs.Button("Hover for a tip", accent="primary")
            bs.Tooltip(tip, "Tooltips can carry accent colors.", accent="primary")
            bs.Button("Show toast", accent="success",
                      on_click=lambda: bs.toast("Operation completed.",
                                                title="Success", accent="success", duration=3000))

        with bs.GroupBox("ContextMenu", horizontal_items="stretch"):
            target = bs.Card(padding=24, horizontal_items="center")
            with target:
                bs.Label("Right-click me", accent="secondary")
            menu = bs.ContextMenu(target=target)
            menu.add_item("Cut", icon="scissors")
            menu.add_item("Copy", icon="copy")
            menu.add_divider()
            menu.add_item("Delete", icon="trash")


def _build_dialogs_page():
    def _ask(fn, *args, **kw):
        result = fn(*args, **kw)
        if result is not None:
            bs.toast(str(result), title="Result", duration=2000)

    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Dialogs & forms", "Prompt for input and edit structured data.")

        with bs.GroupBox("Message & input", layout="row", gap=8):
            bs.Button("alert()", on_click=lambda: bs.alert("Operation complete."))
            bs.Button("confirm()", accent="warning",
                      on_click=lambda: _ask(lambda: bs.confirm("Continue?")))
            bs.Button("ask_string()", on_click=lambda: _ask(bs.ask_string, "Enter your name:"))
            bs.Button("ask_integer()",
                      on_click=lambda: _ask(bs.ask_integer, "Enter age:", min_value=0, max_value=120))

        with bs.GroupBox("Pickers", layout="row", gap=8):
            bs.Button("ask_date()", on_click=lambda: _ask(bs.ask_date, title="Pick a date"))
            bs.Button("ask_color()", on_click=lambda: _ask(bs.ask_color, title="Pick a color"))
            bs.Button("ask_font()", on_click=lambda: _ask(bs.ask_font, title="Pick a font"))
            bs.Button("ask_filter()",
                      on_click=lambda: _ask(bs.ask_filter,
                                            [f"Option {i:02d}" for i in range(20)],
                                            title="Filter", enable_search=True,
                                            enable_select_all=True))

        with bs.GroupBox("Form & FormDialog", horizontal_items="stretch", gap=8):
            bs.Form(
                data={"first_name": "Jane", "last_name": "Doe",
                      "email": "jane@example.com", "active": True},
                col_count=2, min_col_width=220,
            )

            def _show_form():
                dlg = FormDialog(
                    title="Settings",
                    data={"name": "", "email": ""},
                    items=[
                        {"key": "name", "label": "Name"},
                        {"key": "email", "label": "Email"},
                    ],
                )
                dlg.show()
                if dlg.result:
                    bs.toast(str(dlg.result), title="Form Result", duration=3000)

            bs.Button("Open FormDialog", accent="primary", on_click=_show_form)


def _build_design_page():
    with bs.Column(padding=24, gap=16, grow=True, horizontal_items="stretch"):
        _heading("Design system", "Font tokens, icons, themes, and surfaces.")

        with bs.GroupBox("Font tokens", layout="grid", columns=['200px', 1],
                         horizontal_items="left"):
            for token, desc in [
                ("heading-lg", "Heading LG"),
                ("body", "Body (default)"),
                ("caption", "Caption"),
                ("code", "Code"),
            ]:
                bs.Label(desc, font=token)
                bs.Label(f'font="{token}"', font="code", accent="secondary")

        with bs.GroupBox("Icons", layout="row", gap=16, vertical_items="center"):
            for size in (16, 20, 24, 32, 48):
                bs.Label(f"{size}px", icon={"name": "star-fill", "size": size})

        with bs.GroupBox("Theme", horizontal_items="stretch", gap=8):
            style = get_style()
            theme_names = sorted(s["name"] for s in style.theme_provider.list_themes())
            with bs.Row(gap=8, vertical_items="center"):
                bs.Label("Theme:")
                sel = bs.Select(options=theme_names, value=style.current_theme, grow=True)
                sel.on_change(lambda e: sel._internal.after(0, lambda: bs.set_theme(sel.value)))
                bs.ThemeToggle()

        with bs.GroupBox("Surfaces", layout="row", grow_items=True, gap=8):
            for surface in ("chrome", "content", "card", "overlay"):
                with bs.Column(padding=12, horizontal_items="center", surface=surface):
                    bs.Label(surface.title(), surface=surface)


# =============================================================================
# Gallery app
# =============================================================================


def build_gallery_shell(shell) -> None:
    """Populate a Widget Gallery `AppShell` (toolbar, status bar, and pages).

    Shared by `run_demo()` and the docs gallery screenshot so the captured
    gallery always matches the live demo. Pages are lazy-built on first visit.
    """
    with shell.add_toolbar() as bar:
        with bar.add_menu("File") as file_menu:
            file_menu.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with bar.add_menu("View") as view_menu:
            view_menu.add_action("Toggle theme", on_click=bs.toggle_theme)
        bar.add_spacer()
        bar.add_theme_toggle()

    shell.statusbar.add_text("Ready")
    shell.statusbar.add_spacer()
    shell.statusbar.add_text(f"bootstack v{bs.__version__}")

    # Page registry: key → (page_frame, builder)
    _pages: dict[str, tuple[object, object]] = {}

    # A single-tier page nav with the higher-emphasis solid selection.
    nav = shell.page_nav(variant="solid")

    def _register(key, builder, *, text, icon, scrollable=False):
        page = nav.add_page(key, text=text, icon=icon, scrollable=scrollable)
        _pages[key] = (page, builder)

    _register("home", _build_home_page, text="Home", icon="house")

    nav.add_divider()
    nav.add_header("Widgets")
    _register("actions", _build_actions_page, text="Actions", icon="hand-index-thumb", scrollable=True)
    _register("inputs", _build_inputs_page, text="Inputs", icon="input-cursor-text", scrollable=True)
    _register("editing", _build_editing_page, text="Text Editing", icon="code-slash", scrollable=True)
    _register("selection", _build_selection_page, text="Selection", icon="ui-checks", scrollable=True)

    nav.add_divider()
    nav.add_header("Data")
    _register("data", _build_data_page, text="Data Display", icon="speedometer2", scrollable=True)
    _register("tables", _build_tables_page, text="Data Tables", icon="table", scrollable=True)
    _register("media", _build_media_page, text="Media", icon="images", scrollable=True)

    nav.add_divider()
    nav.add_header("Structure")
    _register("layout", _build_layout_page, text="Layout", icon="layout-wtf", scrollable=True)
    _register("navigation", _build_navigation_page, text="Navigation", icon="window-stack", scrollable=True)
    _register("dialogs", _build_dialogs_page, text="Dialogs & Forms", icon="chat-square-text", scrollable=True)

    nav.add_divider()
    nav.add_header("Design System")
    _register("design", _build_design_page, text="Design", icon="palette", scrollable=True)

    # Lazy-build: construct page content only on first visit
    _built: set[str] = set()

    def _build_page(key: str) -> None:
        if key in _built or key not in _pages:
            return
        page, builder = _pages[key]
        with page:
            builder()
        _built.add(key)

    _build_page("home")

    def _on_page_change(event) -> None:
        # on_page_change delivers a PageChangeEvent (unpacked); .page is the key.
        key = getattr(event, "page", None)
        if key:
            _build_page(key)

    shell.on_page_change(_on_page_change)
    shell.navigate("home")


def run_demo():
    """Run the bootstack widget gallery as an AppShell application."""
    with bs.AppShell(
        title="Widget Gallery",
        theme="bootstrap-light",
        size=(1100, 750),
    ) as shell:
        build_gallery_shell(shell)
    shell.run()


def setup_demo(master):
    """Legacy entry point — the gallery now uses AppShell."""
    with bs.Column(parent=master, grow=True, horizontal_items="stretch", padding=40):
        bs.Label(
            "Use 'bootstack gallery' to launch the Widget Gallery.",
            font="heading-lg",
        )
