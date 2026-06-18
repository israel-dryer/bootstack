"""
Widget Gallery

An AppShell-based showcase of bootstack widgets, organized by category.
Each sidebar item opens a page demonstrating a widget group.
"""

import bootstack as bs
from bootstack.signals import Signal
from bootstack.dialogs import FormDialog
from bootstack.style.style import get_style


# =============================================================================
# Page builders — one per sidebar item
# =============================================================================


def _build_home_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("bootstack", font="heading-xl[bold]")
        bs.Label("Modern UI framework for Python", accent="secondary")
        with bs.GroupBox("About This Gallery"):
            bs.Label(
                "Browse the sidebar to explore bootstack widgets by category.\n\n"
                "Each page demonstrates a group of related widgets with\n"
                "color variants, style options, and interactive examples.\n\n"
                "Use the theme toggle in the toolbar or visit the Themes\n"
                "page to try different themes."
            )


# -- Typography ---------------------------------------------------------------


def _build_typography_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Typography", font="heading-xl")
        bs.Label("Semantic font tokens for consistent text styling.", accent="secondary")

        with bs.GroupBox("Font Tokens", layout="grid", columns=['225px', 1], horizontal_items="left"):
            for token, desc in [
                ("display-xl", "Display XL"),
                ("display-lg", "Display LG"),
                ("heading-xl", "Heading XL"),
                ("heading-lg", "Heading LG"),
                ("heading-md", "Heading MD"),
                ("heading-sm", "Heading SM"),
                ("body-xl", "Body XL"),
                ("body-lg", "Body LG"),
                ("body",     "Body (default)"),
                ("body-sm",  "Body SM"),
                ("label",    "Label"),
                ("caption",  "Caption"),
                ("code",     "Code"),
            ]:
                bs.Label(desc, font=token)
                bs.Label(f'font="{token}"', font="code", accent="secondary")

        with bs.GroupBox("Font Modifiers", layout="grid", columns=['225px', 1], horizontal_items="left"):
            for token, desc in [
                ("body[bold]",          "Bold"),
                ("body[italic]",        "Italic"),
                ("body[bold][italic]",  "Bold Italic"),
                ("body[underline]",     "Underline"),
                ("heading-md[bold]",    "Heading Bold"),
            ]:
                bs.Label(desc, font=token)
                bs.Label(f'font="{token}"', font="code", accent="secondary")


# -- Icons --------------------------------------------------------------------


def _build_icons_page():
    icon_names = [
        "house", "gear", "person", "search", "bell",
        "envelope", "heart", "star", "trash", "pencil",
        "folder", "file-earmark-text", "download", "upload", "check-circle",
        "exclamation-triangle", "info-circle", "x-circle", "arrow-left", "arrow-right",
    ]

    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Icons", font="heading-xl")
        bs.Label("Bootstrap Icons via the icon= parameter.", accent="secondary")

        with bs.GroupBox("Common Icons", layout="grid", columns=5, gap=8, horizontal_items="left"):
            for name in icon_names:
                bs.Label(name, icon=name)

        with bs.GroupBox("Icon Sizes", layout="row", gap=16, vertical_items="center"):
            for size in (12, 16, 20, 24, 32, 48):
                bs.Label(f"{size}px", icon={"name": "star-fill", "size": size})

        with bs.GroupBox("Icons in Context", layout="row", gap=16):
            bs.Button("Save",     icon="save")
            bs.Button("Delete",   icon="trash",  accent="danger")
            bs.Button("Settings", icon="gear",   accent="default")
            bs.Button(icon="plus-lg",  icon_only=True, accent="success")
            bs.Button(icon="x-lg",     icon_only=True, accent="danger")


# -- Actions ------------------------------------------------------------------


def _build_buttons_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Actions", font="heading-xl")
        bs.Label("Buttons and button-like widgets for triggering actions.", accent="secondary")

        with bs.GroupBox("Button — Color Variants", grow_items=True, gap=4, layout="row"):
            for color in ("default", "primary", "success", "warning", "danger"):
                bs.Button(color.title(), accent=color)

        with bs.GroupBox("Button — Style Variants", horizontal_items="stretch", gap=6):
            with bs.Row(gap=4, grow_items=True):
                for variant in ("solid", "outline", "ghost"):
                    bs.Button(variant.title(), accent="primary", variant=variant)
            with bs.Row(gap=4, grow_items=True):
                bs.Button("Disabled Solid",   accent="primary",  disabled=True)
                bs.Button("Disabled Outline", accent="default",  variant="outline", disabled=True)

        with bs.GroupBox("ButtonGroup", gap=12, layout="row", horizontal_items="space-between"):
            for accent, variant in [("primary", "solid"), ("danger", "outline"), ("success", "ghost")]:
                bg = bs.ButtonGroup(accent=accent, variant=variant)
                bg.add("Cut",   icon="scissors")
                bg.add("Copy",  icon="copy")
                bg.add("Paste", icon="clipboard")

        with bs.GroupBox("MenuButton", layout="row", gap=12):
            mb = bs.MenuButton("Actions", icon="three-dots", accent="primary")
            mb.add_item("New file", icon="file-earmark")
            mb.add_item("Open…", icon="folder2-open")
            mb.add_divider()
            mb.add_item("Delete", icon="trash")
            mb2 = bs.MenuButton("View", icon="eye", variant="outline")
            mb2.add_item("Zoom in", icon="zoom-in")
            mb2.add_item("Zoom out", icon="zoom-out")


# -- Text Inputs -------------------------------------------------------------


def _build_text_inputs_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Text Inputs", font="heading-xl")
        bs.Label("Specialized entry widgets for text, passwords, and file paths.", accent="secondary")

        with bs.GroupBox("TextField", horizontal_items="stretch", gap=6):
            bs.TextField(label="Name",     message="Enter your full name")
            bs.TextField(label="Email",    message="example@email.com")
            bs.TextField(label="Disabled", value="Read only", disabled=True)

        with bs.GroupBox("PasswordField", horizontal_items="stretch"):
            bs.PasswordField(label="Password", message="Click the eye to toggle")

        with bs.GroupBox("PathField", horizontal_items="stretch", gap=6):
            bs.PathField(label="File",   mode="open", message="Select a file")
            bs.PathField(label="Folder", mode="directory",    message="Select a directory")

        with bs.GroupBox("TextArea", horizontal_items="stretch", grow=True):
            bs.TextArea(
                value=(
                    "TextArea provides a multi-line text input with\n"
                    "automatic scrollbars, undo/redo, and signal binding.\n\n"
                    "Try typing more text to see scrollbars appear!"
                ),
                grow=True,
            )


# -- Code Editor --------------------------------------------------------------


_DEMO_PYTHON = '''\
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


class Counter:
    def __init__(self, start: int = 0):
        self.value = start

    def increment(self) -> None:
        self.value += 1

    def reset(self) -> None:
        self.value = 0


if __name__ == "__main__":
    c = Counter()
    for _ in range(5):
        c.increment()
    print(greet("bootstack"), c.value)
'''

_DEMO_JSON = '''\
{
    "name": "bootstack",
    "version": "1.0.0",
    "description": "Modern UI framework for Python",
    "dependencies": {
        "pillow": ">=10.0",
        "pygments": ">=2.15"
    },
    "scripts": {
        "demo": "python -m bootstack.cli demo"
    }
}
'''


def _build_code_editor_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Code Editor", font="heading-xl")
        bs.Label("Full-featured code editor with syntax highlighting, undo/redo, and search.", accent="secondary")

        with bs.GroupBox("Python", horizontal_items="stretch", gap=6):
            editor = bs.CodeEditor(_DEMO_PYTHON, language="python", height=18)

            dirty_sig = Signal("clean")
            editor.on_modified(lambda e: dirty_sig.set("modified"))
            editor.mark_saved()

            with bs.Row(gap=6, vertical_items="center"):
                bs.Label(text_signal=dirty_sig, accent="secondary")
                bs.Button("Mark saved",  variant="outline", on_click=lambda: (editor.mark_saved(), dirty_sig.set("clean")))
                bs.Button("Undo",        variant="outline", on_click=editor.undo)
                bs.Button("Redo",        variant="outline", on_click=editor.redo)
                bs.Button("Find (⌃F)",   variant="outline", on_click=editor.show_search)

        with bs.GroupBox("JSON — read-only", horizontal_items="stretch"):
            bs.CodeEditor(_DEMO_JSON, language="json", read_only=True, height=14)

        with bs.GroupBox("Language switcher", horizontal_items="stretch", gap=6):
            _SNIPPETS = {
                "python":     "def add(a, b):\n    return a + b\n\nresult = add(1, 2)\nprint(result)\n",
                "json":       '{\n    "language": "json",\n    "active": true,\n    "count": 42\n}\n',
                "sql":        "SELECT name, email\nFROM users\nWHERE active = 1\nORDER BY name ASC;\n",
                "html":       "<section>\n  <h1>Hello</h1>\n  <p>A simple paragraph.</p>\n</section>\n",
                "css":        "body {\n    font-family: sans-serif;\n    background: #f5f5f5;\n    margin: 0;\n}\n",
                "javascript": "function greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconsole.log(greet('world'));\n",
            }

            live_editor = bs.CodeEditor(_SNIPPETS["python"], language="python", height=10)

            def _set_lang(lang: str) -> None:
                live_editor.language = lang
                live_editor.value = _SNIPPETS[lang]

            with bs.Row(gap=4):
                for lang in _SNIPPETS:
                    bs.Button(lang, variant="outline", on_click=lambda l=lang: _set_lang(l))


# -- Numeric & Date -----------------------------------------------------------


def _build_numeric_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Numeric & Date", font="heading-xl")
        bs.Label("Numeric entries, sliders, and date/time pickers.", accent="secondary")

        with bs.GroupBox("NumberField", gap=8, layout="row", grow_items=True):
            bs.NumberField(label="Quantity", value=42,    min_value=0, max_value=100)
            bs.NumberField(label="Price",    value=19.99, step=0.01)

        with bs.GroupBox("SpinnerField", horizontal_items="stretch"):
            bs.SpinnerField(
                label="Month",
                options=["Jan","Feb","Mar","Apr","May","Jun", "Jul","Aug","Sep","Oct","Nov","Dec"],
                value="Jan",
            )

        with bs.GroupBox("Slider", horizontal_items="stretch"):
            bs.Label("Basic:")
            bs.Slider(value=50)
            bs.Label("With value badge:")
            bs.Slider(value=65, show_value=True, tick_step=25)

        with bs.GroupBox("DateField & TimeField", gap=8, layout="row", grow_items=True):
            bs.DateField(label="Date")
            bs.TimeField(label="Time")


# -- Selection ----------------------------------------------------------------


def _build_selection_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Selection", font="heading-xl")
        bs.Label("Checkboxes, switches, radio buttons, toggle groups, and selects.", accent="secondary")

        with bs.GroupBox("Checkbox & Switch", gap=8, layout="grid", columns=6):
            bs.Checkbox("Default", accent="primary", value=True)
            bs.Checkbox("Success", accent="success", value=False)
            bs.Checkbox("Disabled", disabled=True)
            bs.Switch("Notifications", accent="primary", value=True)
            bs.Switch("Dark Mode",     accent="success")
            bs.Switch("Disabled",      disabled=True)

        with bs.GroupBox("RadioGroup"):
            rg = bs.RadioGroup(value="opt1", accent="primary")
            rg.add("Option 1", value="opt1")
            rg.add("Option 2", value="opt2")
            rg.add("Option 3", value="opt3")

        with bs.GroupBox("ToggleGroup", gap=6, layout="grid", columns=2):
            with bs.Column():
                bs.Label("Single select:")
                tg = bs.ToggleGroup(mode="single", accent="primary", variant="outline", value="B")
                tg.add("Bold",      value="B")
                tg.add("Italic",    value="I")
                tg.add("Underline", value="U")
            with bs.Column():
                bs.Label("Multi select:")
                tg2 = bs.ToggleGroup(mode="multi", accent="success", variant="outline")
                tg2.add("Python",     value="python")
                tg2.add("JavaScript", value="javascript")
                tg2.add("Rust",       value="rust")

        with bs.GroupBox("Select & SelectButton", horizontal_items="stretch", gap=8):
            bs.Select(
                label="Size:",
                options=["Small", "Medium", "Large", "Extra Large"],
                value="Medium",
            )
            with bs.Row(gap=8):
                bs.SelectButton(options=["Day", "Week", "Month"], value="Week", accent="primary")
                bs.SelectButton(options=["Light", "Dark", "System"], value="System", variant="outline")

        with bs.GroupBox("ToggleButton", layout="row", gap=8):
            bs.ToggleButton("Bold", value=True)
            bs.ToggleButton("Italic")
            bs.ToggleButton("Mute", icon="volume-mute")

        with bs.GroupBox("RadioToggleButton (segmented)", layout="row", gap=0):
            view = Signal("grid")
            bs.RadioToggleButton("Grid",  "grid",  signal=view)
            bs.RadioToggleButton("List",  "list",  signal=view)
            bs.RadioToggleButton("Cards", "cards", signal=view)


# -- Calendar -----------------------------------------------------------------


def _build_calendar_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Calendar", font="heading-xl")
        bs.Label("Interactive date picker.", accent="secondary")

        with bs.Row(gap=12):
            with bs.GroupBox("Single Selection"):
                bs.Calendar(accent="primary")

            with bs.GroupBox("Range Selection"):
                bs.Calendar(selection_mode="range", accent="success")


# -- Forms --------------------------------------------------------------------


def _build_forms_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Forms", font="heading-xl")
        bs.Label("Spec-driven form builder for consistent data-entry UIs.", accent="secondary")

        bs.Label("Inferred Form", font="body[bold]")
        bs.Form(
            data={
                "first_name": "Jane", "last_name": "Doe",
                "age": 34, "email": "jane@example.com",
                "salary": 120000.50, "active": True,
            },
            col_count=2, min_col_width=220,
        )

        bs.Label("Explicit Layout", font="body[bold]")
        bs.Form(
            data={"username": "jdoe", "role": "Admin", "newsletter": True},
            items=[
                {
                    "type": "group", "label": "Profile", "col_count": 2,
                    "items": [
                        {"key": "username", "label": "Username"},
                        {"key": "password", "label": "Password", "editor": "passwordentry"},
                        {"key": "role", "label": "Role", "editor": "selectbox",
                         "items": ["Admin", "User", "Viewer"]},
                    ],
                },
                {
                    "type": "group", "label": "Preferences",
                    "items": [
                        {"key": "newsletter", "label": "Newsletter", "editor": "switch"},
                    ],
                },
            ],
        )


# -- Data Display -------------------------------------------------------------


def _build_data_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Data Display", font="heading-xl")
        bs.Label("Labels, badges, and a full-featured data table for presenting data.", accent="secondary")

        with bs.GroupBox("Labels", layout="row", gap=4):
            for color in ("primary", "secondary", "success", "warning", "danger"):
                bs.Label(color.title(), accent=color, padding=(8, 4))

        with bs.GroupBox("Badges", gap=16, layout="row"):
            for color in ("primary", "secondary", "success", "warning", "danger"):
                bs.Badge(color.title(), accent=color)

            bs.Badge("Pill",  accent="primary", variant="pill")
            bs.Badge("99+",   accent="danger",  variant="pill")
            bs.Badge("New",   accent="success")

        with bs.GroupBox("ListView"):
            bs.ListView(
                items=[
                    {"id": 1, "title": "Inbox",   "text": "12 unread messages",   "icon": "inbox",        "badge": "12"},
                    {"id": 2, "title": "Starred", "text": "Flagged for follow-up", "icon": "star-fill"},
                    {"id": 3, "title": "Sent",    "text": "Your sent mail",        "icon": "send"},
                    {"id": 4, "title": "Drafts",  "text": "1 unfinished draft",    "icon": "file-earmark", "badge": "1"},
                    {"id": 5, "title": "Archive", "text": "240 archived items",    "icon": "archive"},
                ],
                selection_mode="single",
                height=200,
            )

        with bs.GroupBox("DataTable", horizontal_items="stretch", grow=True):
            employees = [
                {"name": "Ada Lovelace",      "role": "Staff Engineer",     "dept": "Engineering", "salary": 185000},
                {"name": "Alan Turing",       "role": "Software Engineer",  "dept": "Engineering", "salary": 162000},
                {"name": "Grace Hopper",      "role": "Engineering Lead",   "dept": "Engineering", "salary": 198000},
                {"name": "Katherine Johnson", "role": "Data Scientist",     "dept": "Engineering", "salary": 171000},
                {"name": "Carol Williams",    "role": "Product Designer",   "dept": "Design",      "salary": 142000},
                {"name": "David Kim",         "role": "Product Designer",   "dept": "Design",      "salary": 138000},
                {"name": "Eva Martinez",      "role": "Account Executive",  "dept": "Sales",       "salary": 129000},
                {"name": "Frank Wong",        "role": "Sales Manager",      "dept": "Sales",       "salary": 156000},
                {"name": "Grace Lee",         "role": "Support Specialist", "dept": "Support",     "salary": 98000},
                {"name": "Henry Ford",        "role": "Support Specialist", "dept": "Support",     "salary": 96000},
                {"name": "Iris Chen",         "role": "Content Strategist", "dept": "Marketing",   "salary": 112000},
                {"name": "Jack Brown",        "role": "Growth Marketer",    "dept": "Marketing",   "salary": 118000},
            ]
            bs.DataTable(
                columns=[
                    {"text": "Name",       "key": "name",   "width": 200},
                    {"text": "Role",       "key": "role",   "width": 180},
                    {"text": "Department", "key": "dept",   "width": 140},
                    {"text": "Salary",     "key": "salary", "width": 120, "anchor": "e", "format": "${:,.0f}"},
                ],
                rows=employees,
                selection_mode="multi",
                show_selection_controls=True,
                allow_filter=True,
                allow_group=True,
                allow_export=True,
                page_size=8,
                grow=True,
            )

        with bs.GroupBox("Tree"):
            bs.Tree(
                nodes=[
                    {
                        "label": "Engineering",
                        "open_icon": "folder2-open", "closed_icon": "folder-fill",
                        "expanded": True,
                        "children": [
                            {"label": "Ada Lovelace",  "icon": "person-fill"},
                            {"label": "Alan Turing",    "icon": "person-fill"},
                            {"label": "Grace Hopper",   "icon": "person-fill"},
                        ],
                    },
                    {
                        "label": "Design",
                        "open_icon": "folder2-open", "closed_icon": "folder-fill",
                        "expanded": True,
                        "children": [
                            {"label": "Carol Williams", "icon": "person-fill"},
                            {"label": "David Kim",      "icon": "person-fill"},
                        ],
                    },
                    {
                        "label": "Sales",
                        "open_icon": "folder2-open", "closed_icon": "folder-fill",
                        "children": [
                            {"label": "Eva Martinez", "icon": "person-fill"},
                            {"label": "Frank Wong",   "icon": "person-fill"},
                        ],
                    },
                ],
                selection_mode="multi",
                show_selection_controls=True,
                height=320,
            )


# -- Progress & Meters --------------------------------------------------------


def _build_progress_page():
    slider_value = Signal(65.0)

    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Progress & Meters", font="heading-xl")
        bs.Label("Progress bars and gauges for showing values and status.", accent="secondary")

        with bs.GroupBox("Slider (drag to control progress bars)", horizontal_items="stretch"):
            bs.Slider(min_value=0, max_value=100, signal=slider_value)

        with bs.GroupBox("RangeSlider", horizontal_items="stretch"):
            bs.RangeSlider(low_value=25, high_value=75, min_value=0, max_value=100,
                           show_value=True, accent="primary")

        with bs.GroupBox("ProgressBar", horizontal_items="stretch", gap=8):
            bs.ProgressBar(signal=slider_value, max_value=100)
            bs.ProgressBar(value=75,  max_value=100, accent="success")
            bs.ProgressBar(value=45,  max_value=100, accent="danger")
            bs.ProgressBar(value=30,  max_value=100, accent="warning")

        with bs.GroupBox("Gauge"):
            with bs.Row(gap=16, vertical_items="center"):
                for amount, label, color in [
                    (45, "CPU Usage", "primary"),
                    (78, "Memory",    "warning"),
                    (92, "Disk",      "danger"),
                ]:
                    bs.Gauge(
                        value=amount, max_value=100,
                        subtitle=label, accent=color,
                        interactive=True,
                    )


# -- Layout -------------------------------------------------------------------


def _build_layout_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Layout", font="heading-xl")
        bs.Label("Containers, expandable panels, and split panes.", accent="secondary")

        with bs.GroupBox("Card", layout="row", grow_items=True, gap=16):
            for title, body, color in [
                ("Users",   "1,234 active", "primary"),
                ("Revenue", "$45,678",       "success"),
                ("Errors",  "12 today",      "danger"),
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
            with acc.add("Section 3"):
                bs.Label("Content for section three.")

        with bs.GroupBox("SplitView", horizontal_items="stretch", grow=True):
            sv = bs.SplitView(orient="horizontal", grow=True)
            with sv.add(padding=10, horizontal_items="center"):
                bs.Label("Left Pane")
                bs.Label("Drag the sash to resize", accent="secondary", font="caption")
            with sv.add(padding=10, horizontal_items="center"):
                bs.Label("Right Pane")
                bs.Label("Both panes are resizable", accent="secondary", font="caption")

        with bs.GroupBox("ScrollView", horizontal_items="stretch"):
            bs.Label("A fixed-height region that scrolls its overflow:", accent="secondary")
            with bs.ScrollView(height=140, show_border=True, padding=8):
                for i in range(20):
                    bs.Label(f"Scrollable row {i + 1}")

        with bs.GroupBox("Divider", horizontal_items="stretch", gap=8):
            bs.Divider()
            bs.Divider(accent="primary")
            bs.Divider(accent="success")
            bs.Divider(accent="danger")


# -- Navigation ---------------------------------------------------------------


def _build_navigation_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Navigation", font="heading-xl")
        bs.Label("Tab-based navigation widgets.", accent="secondary")

        with bs.GroupBox("Tabs (horizontal)", horizontal_items="stretch", grow=True):
            tabs = bs.Tabs(grow=True)
            with tabs.add("dashboard", label="Dashboard", icon="house"):
                bs.Label("Dashboard content goes here.", padding=20)
            with tabs.add("files", label="Files", icon="folder2"):
                bs.Label("Browse your files here.", padding=20)
            with tabs.add("settings", label="Settings", icon="gear"):
                bs.Label("Configure your settings.", padding=20)

        with bs.GroupBox("Tabs (closable + addable)", horizontal_items="stretch", grow=True):
            tabs2 = bs.Tabs(allow_close=True, allow_add=True, grow=True)
            _doc_n = [1]
            with tabs2.add("doc1", label="Document 1", icon="file-text"):
                bs.Label("Content for Document 1.", padding=20)

            def _add_doc():
                _doc_n[0] += 1
                n = _doc_n[0]
                page = tabs2.add(f"doc{n}", label=f"Document {n}", icon="file-text")
                with page:
                    bs.Label(f"Content for Document {n}.", padding=20)
                page.select()  # newly added tab becomes active (and scrolls into view)

            tabs2.on_tab_add(lambda e: _add_doc())

        with bs.GroupBox("Tabs (overflow scrolls + menu, max 16)", horizontal_items="stretch", grow=True):
            tabs3 = bs.Tabs(allow_close="hover", allow_add=True, max_tabs=16, grow=True)
            _file_n = [0]

            def _add_file(select=True):
                _file_n[0] += 1
                n = _file_n[0]
                page = tabs3.add(f"file{n}", label=f"source-file-{n}.py", icon="file-earmark-code")
                with page:
                    bs.Label(f"Contents of source-file-{n}.py", padding=20)
                if select:
                    page.select()

            for _ in range(12):
                _add_file(select=False)
            tabs3.on_tab_add(lambda e: _add_file())

        with bs.GroupBox("Tabs (vertical overflow)", horizontal_items="stretch", grow=True):
            tabs4 = bs.Tabs(orient="vertical", grow=True)
            for n in range(1, 13):
                with tabs4.add(f"sec{n}", label=f"Section {n}", icon="bookmark"):
                    bs.Label(f"Section {n} body", padding=20)

        with bs.GroupBox("PageStack (swap content in place)", horizontal_items="stretch", grow=True):
            ps = bs.PageStack(grow=True)
            with ps.add("welcome"):
                bs.Label("Welcome page", font="heading-md", padding=20)
            with ps.add("details"):
                bs.Label("Details page", font="heading-md", padding=20)
            with ps.add("done"):
                bs.Label("All done!", font="heading-md", padding=20)
            with bs.Row(gap=8):
                bs.Button("Welcome", on_click=lambda: ps.navigate("welcome"))
                bs.Button("Details", on_click=lambda: ps.navigate("details"))
                bs.Button("Done",    on_click=lambda: ps.navigate("done"))


# -- Overlays -----------------------------------------------------------------


def _build_overlays_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Overlays", font="heading-xl")
        bs.Label("Tooltips, the toast/notification/snackbar message family, and context menus.",
                 accent="secondary")

        with bs.GroupBox("Tooltip"):
            bs.Label("Hover over the buttons below:")
            with bs.Row(gap=8):
                b1 = bs.Button("Default",  accent="primary")
                b2 = bs.Button("Accented", accent="primary")
                b3 = bs.Button("Long tip", accent="default")
            bs.Tooltip(b1, "This is a basic tooltip.")
            bs.Tooltip(b2, "Tooltips can have accent colors.", accent="primary")
            bs.Tooltip(b3, "This is a longer tooltip that wraps. "
                           "It shows how tooltips handle multi-line content.",
                       wrap_width=200)

        with bs.GroupBox("Toast"):
            bs.Label("Click buttons to show toast notifications:")

            def show_toast(title, message, accent):
                bs.toast(message, title=title, accent=accent, duration=3000)

            with bs.Row(gap=8):
                bs.Button("Success", accent="success",
                          on_click=lambda: show_toast("Success", "Operation completed.", "success"))
                bs.Button("Warning", accent="warning",
                          on_click=lambda: show_toast("Warning", "Check your settings.", "warning"))
                bs.Button("Error",   accent="danger",
                          on_click=lambda: show_toast("Error", "Something went wrong.", "danger"))

        with bs.GroupBox("Notification & Snackbar", gap=8):
            bs.Label("Persistent corner notification, and an in-app snackbar with one action:",
                     accent="secondary")
            with bs.Row(gap=8):
                bs.Button("Notification", on_click=lambda: bs.Notification(
                    "Backup complete", message="3.2 GB uploaded to the cloud.",
                    detail="just now", icon="cloud-check", accent="success").show())
                bs.Button("Snackbar (Undo)", on_click=lambda: bs.snackbar(
                    "Conversation archived.", action="Undo"))

        with bs.GroupBox("ContextMenu", horizontal_items="stretch", gap=8):
            bs.Label("Right-click the area below:", accent="secondary")
            target = bs.Card(padding=24, horizontal_items="center")
            with target:
                bs.Label("Right-click me", accent="secondary")
            menu = bs.ContextMenu(target=target)
            menu.add_item("Cut", icon="scissors")
            menu.add_item("Copy", icon="copy")
            menu.add_item("Paste", icon="clipboard")
            menu.add_divider()
            menu.add_item("Delete", icon="trash")


# -- Dialogs ------------------------------------------------------------------


def _build_dialogs_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Dialogs", font="heading-xl")
        bs.Label("Click buttons to launch dialog types.", accent="secondary")

        with bs.GroupBox("Alert & Confirm"):
            with bs.Row(gap=8):
                bs.Button("alert()",   on_click=lambda: bs.alert("Operation complete."))
                bs.Button("confirm()", accent="warning",
                          on_click=lambda: bs.toast(
                              f"confirm() returned {bs.confirm('Continue?')}",
                              title="Result", duration=2000,
                          ))

        def _ask(fn, *args, **kw):
            result = fn(*args, **kw)
            if result is not None:
                bs.toast(str(result), title="Result", duration=2000)

        with bs.GroupBox("Input Dialogs"):
            with bs.Row(gap=8):
                bs.Button("ask_string()",
                          on_click=lambda: _ask(bs.ask_string, "Enter your name:"))
                bs.Button("ask_integer()",
                          on_click=lambda: _ask(bs.ask_integer, "Enter age:", min_value=0, max_value=120))
                bs.Button("ask_float()",
                          on_click=lambda: _ask(bs.ask_float, "Enter amount:"))
                bs.Button("ask_item()",
                          on_click=lambda: _ask(bs.ask_item, "Pick one:",
                                                ["Small", "Medium", "Large"]))

        with bs.GroupBox("Date Dialogs"):
            with bs.Row(gap=8):
                bs.Button("ask_date()",
                          on_click=lambda: _ask(bs.ask_date, title="Pick a date"))
                bs.Button("ask_date_range()",
                          on_click=lambda: _ask(bs.ask_date_range, title="Pick a range"))

        with bs.GroupBox("Pickers & Filter"):
            with bs.Row(gap=8):
                bs.Button("ask_color()",
                          on_click=lambda: _ask(bs.ask_color, title="Pick a color"))
                bs.Button("ask_font()",
                          on_click=lambda: _ask(bs.ask_font, title="Pick a font"))
                bs.Button("ask_filter()",
                          on_click=lambda: _ask(
                              bs.ask_filter,
                              [f"Option {i:02d}" for i in range(30)],
                              title="Filter", enable_search=True,
                              enable_select_all=True))

        with bs.GroupBox("FormDialog"):
            def _show_form():
                dlg = FormDialog(
                    title="Settings",
                    data={"name": "", "email": ""},
                    items=[
                        {"key": "name",  "label": "Name"},
                        {"key": "email", "label": "Email"},
                    ],
                )
                dlg.show()
                if dlg.result:
                    bs.toast(str(dlg.result), title="Form Result", duration=3000)

            bs.Button("Open FormDialog", accent="primary", on_click=_show_form)


# -- Themes -------------------------------------------------------------------


def _build_theme_page():
    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Themes", font="heading-xl")
        bs.Label("Switch themes to see all widgets update in real time.", accent="secondary")

        with bs.GroupBox("Theme Selector", layout="grid", columns=2):
            style = get_style()
            theme_names = sorted(s["name"] for s in style.theme_provider.list_themes())

            with bs.Row(gap=8):
                bs.Label("Theme:", width=10)
                sel = bs.Select(options=theme_names, value=style.current_theme, grow=True)
                sel.on_change(lambda e: sel._internal.after(0, lambda: bs.set_theme(sel.value)))

            with bs.Row(gap=8):
                bs.Label("Quick:", width=10)
                bs.ThemeToggle()

        with bs.GroupBox("Accent Colors"):
            with bs.Row(gap=4, grow_items=True):
                for color in ("primary", "secondary", "info", "success", "warning", "danger"):
                    bs.Button(color.title(), accent=color)

        with bs.GroupBox("Surfaces"):
            with bs.Row(gap=4, grow_items=True):
                for surface in ("chrome", "content", "card", "overlay", "input"):
                    with bs.Column(padding=12, horizontal_items="center", surface=surface):
                        bs.Label(surface.title(), surface=surface)


# -- Media --------------------------------------------------------------------


def _demo_photos():
    """A few solid-color tiles as `Image` handles, for the media widgets."""
    from PIL import Image as _PILImage
    from bootstack.images import Image

    swatches = [
        ("Sunset", (244, 114, 82)),
        ("Ocean",  (56, 132, 222)),
        ("Forest", (71, 159, 118)),
        ("Berry",  (176, 42, 88)),
        ("Amber",  (240, 180, 41)),
        ("Slate",  (90, 99, 110)),
    ]
    return [
        {"title": name, "image": Image.from_pil(_PILImage.new("RGB", (320, 320), rgb))}
        for name, rgb in swatches
    ]


def _build_media_page():
    from bootstack.images import get_icon

    photos = _demo_photos()

    with bs.Column(padding=20, gap=12, grow=True, horizontal_items="stretch"):
        bs.Label("Media", font="heading-xl")
        bs.Label("Identity badges, images, thumbnail grids, and carousels.", accent="secondary")

        with bs.GroupBox("Avatar", layout="row", gap=12):
            bs.Avatar(name="Ada Lovelace")
            bs.Avatar(name="Grace Hopper", shape="rounded")
            bs.Avatar(initials="JS", shape="square")
            bs.Avatar(image=get_icon("person-fill", size=40))

        with bs.GroupBox("Picture", layout="row", gap=16):
            bs.Picture(photos[0]["image"], width=180, height=120, fit="cover", corner_radius=8)
            bs.Picture(photos[1]["image"], width=180, height=120, fit="contain")
            bs.Picture(photos[2]["image"], width=120, height=120, fit="cover", corner_radius=60)

        with bs.GroupBox("Carousel", horizontal_items="stretch"):
            bs.Carousel(items=photos, image_field="image", caption_field="title",
                        fit="cover")

        # Gallery last: it scrolls internally and swallows the wheel event, so
        # keeping it at the bottom leaves the carousel/picture rows above it as
        # places to grab and scroll the page itself.
        with bs.GroupBox("Gallery", horizontal_items="stretch", grow=True):
            bs.Gallery(items=photos, image_field="image", caption_field="title",
                       tile_size=(120, 120), grow=True)


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

    def _register(key, builder, *, text, icon, scrollable=False):
        page = shell.add_page(key, text=text, icon=icon, scrollable=scrollable)
        _pages[key] = (page, builder)

    _register("home",       _build_home_page,       text="Home",        icon="house")

    shell.add_divider()
    shell.add_header("Actions")
    _register("buttons",    _build_buttons_page,    text="Buttons",     icon="hand-index-thumb",   scrollable=True)

    shell.add_divider()
    shell.add_header("Inputs")
    _register("text-inputs",  _build_text_inputs_page,  text="Text Inputs",  icon="input-cursor-text", scrollable=True)
    _register("numeric",      _build_numeric_page,      text="Numeric & Date", icon="123",             scrollable=True)
    _register("forms",        _build_forms_page,        text="Forms",        icon="journal-text",      scrollable=True)
    _register("code-editor",  _build_code_editor_page,  text="Code Editor",  icon="code-slash",        scrollable=True)

    shell.add_divider()
    shell.add_header("Selection")
    _register("selection",  _build_selection_page,  text="Selection",   icon="ui-checks",          scrollable=True)
    _register("calendar",   _build_calendar_page,   text="Calendar",    icon="calendar3",          scrollable=True)

    shell.add_divider()
    shell.add_header("Data Display")
    _register("data",       _build_data_page,       text="Data Tables", icon="table",              scrollable=True)
    _register("progress",   _build_progress_page,   text="Progress",    icon="speedometer2",       scrollable=True)

    shell.add_divider()
    shell.add_header("Media")
    _register("media",      _build_media_page,      text="Media",       icon="images",             scrollable=True)

    shell.add_divider()
    shell.add_header("Layout")
    _register("layout",     _build_layout_page,     text="Containers",  icon="layout-wtf",         scrollable=True)
    _register("navigation", _build_navigation_page, text="Navigation",  icon="window-stack",       scrollable=True)

    shell.add_divider()
    shell.add_header("Overlays & Dialogs")
    _register("overlays",   _build_overlays_page,   text="Overlays",    icon="layers",             scrollable=True)
    _register("dialogs",    _build_dialogs_page,    text="Dialogs",     icon="chat-square-text",   scrollable=True)

    shell.add_divider()
    shell.add_header("Design System")
    _register("themes",     _build_theme_page,      text="Themes",      icon="palette",            scrollable=True)
    _register("typography", _build_typography_page, text="Typography",  icon="fonts",              scrollable=True)
    _register("icons",      _build_icons_page,      text="Icons",       icon="grid-3x3-gap",       scrollable=True)

    # Lazy-build: construct page content only on first visit
    _built: set[str] = set()

    def _build_page(key: str) -> None:
        if key in _built or key not in _pages:
            return
        page, builder = _pages[key]
        with page:
            builder()
        _built.add(key)

    # Build home page immediately; all others on first navigation
    _build_page("home")

    def _on_page_change(event) -> None:
        # on_page_change delivers a PageChangeEvent (unpacked); .page is the
        # key of the now-active page.
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
        nav_variant="solid"
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