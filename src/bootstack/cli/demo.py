"""
Widget Gallery

An AppShell-based showcase of bootstack widgets, organized by category.
Each sidebar item opens a page demonstrating a widget group.
"""

import bootstack as bs
from bootstack.signals import Signal


# =============================================================================
# Page builders — one per sidebar item
# =============================================================================


def _build_home_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("bootstack", font="heading-xl[bold]")
        bs.Label("Modern UI framework for Python", accent="secondary")
        with bs.GroupBox("About This Gallery", fill="horizontal"):
            bs.Label(
                "Browse the sidebar to explore bootstack widgets by category.\n\n"
                "Each page demonstrates a group of related widgets with\n"
                "color variants, style options, and interactive examples.\n\n"
                "Use the theme toggle in the toolbar or visit the Themes\n"
                "page to try different themes."
            )


# -- Typography ---------------------------------------------------------------


def _build_typography_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Typography", font="heading-xl")
        bs.Label("Semantic font tokens for consistent text styling.", accent="secondary")

        with bs.GroupBox("Font Tokens", fill="horizontal", layout="grid", columns=['225px', 1], sticky_items="w"):
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

        with bs.GroupBox("Font Modifiers", fill="horizontal", layout="grid", columns=['225px', 1], sticky_items="w"):
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

    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Icons", font="heading-xl")
        bs.Label("Bootstrap Icons via the icon= parameter.", accent="secondary")

        with bs.GroupBox("Common Icons", fill="horizontal", layout="grid", columns=5, gap=8, sticky_items="w"):
            for name in icon_names:
                bs.Label(name, icon=name)

        with bs.GroupBox("Icon Sizes", fill="horizontal", layout="hstack", gap=16):
            for size in (12, 16, 20, 24, 32, 48):
                bs.Label(f"{size}px", icon={"name": "star-fill", "size": size})

        with bs.GroupBox("Icons in Context", fill="horizontal", layout="hstack", gap=16):
            bs.Button("Save",     icon="save")
            bs.Button("Delete",   icon="trash",  accent="danger")
            bs.Button("Settings", icon="gear",   accent="default")
            bs.Button(icon="plus-lg",  icon_only=True, accent="success")
            bs.Button(icon="x-lg",     icon_only=True, accent="danger")


# -- Actions ------------------------------------------------------------------


def _build_buttons_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Actions", font="heading-xl")
        bs.Label("Buttons and button-like widgets for triggering actions.", accent="secondary")

        with bs.GroupBox("Button — Color Variants", fill="x", expand_items=True, fill_items="x", gap=4, layout="hstack"):
            for color in ("default", "primary", "success", "warning", "danger"):
                bs.Button(color.title(), accent=color)

        with bs.GroupBox("Button — Style Variants", fill="horizontal", gap=6):
            with bs.HStack(gap=4, fill="horizontal", fill_items="horizontal", expand_items=True):
                for variant in ("solid", "outline", "ghost"):
                    bs.Button(variant.title(), accent="primary", variant=variant)
            with bs.HStack(gap=4, fill="horizontal", fill_items="horizontal", expand_items=True):
                bs.Button("Disabled Solid",   accent="primary",  disabled=True)
                bs.Button("Disabled Outline", accent="default",  variant="outline", disabled=True)

        with bs.GroupBox("ButtonGroup", fill="horizontal", gap=12, layout="hstack"):
            for accent, variant in [("primary", "solid"), ("danger", "outline"), ("success", "ghost")]:
                bg = bs.ButtonGroup(accent=accent, variant=variant)
                bg.add("Cut",   icon="scissors")
                bg.add("Copy",  icon="copy")
                bg.add("Paste", icon="clipboard")


# -- Text Inputs -------------------------------------------------------------


def _build_text_inputs_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Text Inputs", font="heading-xl")
        bs.Label("Specialized entry widgets for text, passwords, and file paths.", accent="secondary")

        with bs.GroupBox("TextField", fill="horizontal", gap=6):
            bs.TextField(label="Name",     message="Enter your full name",  fill="horizontal")
            bs.TextField(label="Email",    message="example@email.com",     fill="horizontal")
            bs.TextField(label="Disabled", value="Read only", disabled=True, fill="horizontal")

        with bs.GroupBox("PasswordField", fill="horizontal"):
            bs.PasswordField(label="Password", message="Click the eye to toggle", fill="horizontal")

        with bs.GroupBox("PathField", fill="horizontal", gap=6):
            bs.PathField(label="File",   mode="open", message="Select a file",      fill="horizontal")
            bs.PathField(label="Folder", mode="directory",    message="Select a directory", fill="horizontal")

        with bs.GroupBox("TextArea", fill="both", expand=True):
            bs.TextArea(
                value=(
                    "TextArea provides a multi-line text input with\n"
                    "automatic scrollbars, undo/redo, and signal binding.\n\n"
                    "Try typing more text to see scrollbars appear!"
                ),
                fill="both", expand=True,
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
    with bs.VStack(padding=20, gap=12, fill="x", fill_items="x"):
        bs.Label("Code Editor", font="heading-xl")
        bs.Label("Full-featured code editor with syntax highlighting, undo/redo, and search.", accent="secondary")

        with bs.GroupBox("Python", fill="x", gap=6):
            editor = bs.CodeEditor(_DEMO_PYTHON, language="python", height=18, fill="x")

            dirty_sig = Signal("clean")
            editor.on_modified(lambda e: dirty_sig.set("modified"))
            editor.mark_saved()

            with bs.HStack(gap=6, anchor_items="center"):
                bs.Label(text_signal=dirty_sig, accent="secondary")
                bs.Button("Mark saved",  variant="outline", on_click=lambda: (editor.mark_saved(), dirty_sig.set("clean")))
                bs.Button("Undo",        variant="outline", on_click=editor.undo)
                bs.Button("Redo",        variant="outline", on_click=editor.redo)
                bs.Button("Find (⌃F)",   variant="outline", on_click=editor.show_search)

        with bs.GroupBox("JSON — read-only", fill="x"):
            bs.CodeEditor(_DEMO_JSON, language="json", read_only=True, height=14, fill="x")

        with bs.GroupBox("Language switcher", fill="x", gap=6):
            _SNIPPETS = {
                "python":     "def add(a, b):\n    return a + b\n\nresult = add(1, 2)\nprint(result)\n",
                "json":       '{\n    "language": "json",\n    "active": true,\n    "count": 42\n}\n',
                "sql":        "SELECT name, email\nFROM users\nWHERE active = 1\nORDER BY name ASC;\n",
                "html":       "<section>\n  <h1>Hello</h1>\n  <p>A simple paragraph.</p>\n</section>\n",
                "css":        "body {\n    font-family: sans-serif;\n    background: #f5f5f5;\n    margin: 0;\n}\n",
                "javascript": "function greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconsole.log(greet('world'));\n",
            }

            live_editor = bs.CodeEditor(_SNIPPETS["python"], language="python", height=10, fill="x")

            def _set_lang(lang: str) -> None:
                live_editor.language = lang
                live_editor.value = _SNIPPETS[lang]

            with bs.HStack(gap=4):
                for lang in _SNIPPETS:
                    bs.Button(lang, variant="outline", on_click=lambda l=lang: _set_lang(l))


# -- Numeric & Date -----------------------------------------------------------


def _build_numeric_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Numeric & Date", font="heading-xl")
        bs.Label("Numeric entries, sliders, and date/time pickers.", accent="secondary")

        with bs.GroupBox("NumberField", fill="horizontal", gap=8, layout="hstack", fill_items="x", expand_items=True):
            bs.NumberField(label="Quantity", value=42,    min_value=0, max_value=100)
            bs.NumberField(label="Price",    value=19.99, step=0.01)

        with bs.GroupBox("SpinnerField", fill="horizontal"):
            bs.SpinnerField(
                label="Month",
                options=["Jan","Feb","Mar","Apr","May","Jun", "Jul","Aug","Sep","Oct","Nov","Dec"],
                value="Jan", fill="horizontal",
            )

        with bs.GroupBox("Slider", fill="horizontal"):
            bs.Label("Basic:")
            bs.Slider(value=50, fill="horizontal")
            bs.Label("With value badge:")
            bs.Slider(value=65, show_value=True, tick_step=25, fill="horizontal")

        with bs.GroupBox("DateField & TimeField", fill="x", gap=8, fill_items="x", expand_items=True, layout="hstack"):
            bs.DateField(label="Date")
            bs.TimeField(label="Time")


# -- Selection ----------------------------------------------------------------


def _build_selection_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Selection", font="heading-xl")
        bs.Label("Checkboxes, switches, radio buttons, toggle groups, and selects.", accent="secondary")

        with bs.GroupBox("Checkbox & Switch", fill="x", gap=8, layout="grid", columns=6):
            bs.Checkbox("Default", accent="primary", value=True)
            bs.Checkbox("Success", accent="success", value=False)
            bs.Checkbox("Disabled", disabled=True)
            bs.Switch("Notifications", accent="primary", value=True)
            bs.Switch("Dark Mode",     accent="success")
            bs.Switch("Disabled",      disabled=True)

        with bs.GroupBox("RadioGroup", fill="horizontal"):
            rg = bs.RadioGroup(value="opt1", accent="primary")
            rg.add("Option 1", value="opt1")
            rg.add("Option 2", value="opt2")
            rg.add("Option 3", value="opt3")

        with bs.GroupBox("ToggleGroup", fill="horizontal", gap=6, layout="grid", columns=2):
            with bs.VStack():
                bs.Label("Single select:")
                tg = bs.ToggleGroup(mode="single", accent="primary", variant="outline", value="B")
                tg.add("Bold",      value="B")
                tg.add("Italic",    value="I")
                tg.add("Underline", value="U")
            with bs.VStack():
                bs.Label("Multi select:")
                tg2 = bs.ToggleGroup(mode="multi", accent="success", variant="outline")
                tg2.add("Python",     value="python")
                tg2.add("JavaScript", value="javascript")
                tg2.add("Rust",       value="rust")

        with bs.GroupBox("Select", fill="horizontal"):
            bs.Select(
                label="Size:",
                options=["Small", "Medium", "Large", "Extra Large"],
                value="Medium", fill="horizontal",
            )


# -- Calendar -----------------------------------------------------------------


def _build_calendar_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True):
        bs.Label("Calendar", font="heading-xl")
        bs.Label("Interactive date picker.", accent="secondary")

        with bs.GroupBox("Single Selection", fill="horizontal"):
            bs.Calendar(accent="primary")

        with bs.GroupBox("Range Selection", fill="horizontal"):
            bs.Calendar(selection_mode="range", accent="success")


# -- Forms --------------------------------------------------------------------


def _build_forms_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
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
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Data Display", font="heading-xl")
        bs.Label("Labels, badges, and a full-featured data table for presenting data.", accent="secondary")

        with bs.GroupBox("Labels", fill="horizontal", layout="hstack", gap=4):
            for color in ("primary", "secondary", "success", "warning", "danger"):
                bs.Label(color.title(), accent=color, padding=(8, 4))

        with bs.GroupBox("Badges", fill="x", gap=16, layout="hstack"):
            for color in ("primary", "secondary", "success", "warning", "danger"):
                bs.Badge(color.title(), accent=color)

            bs.Badge("Pill",  accent="primary", variant="pill")
            bs.Badge("99+",   accent="danger",  variant="pill")
            bs.Badge("New",   accent="success")

        with bs.GroupBox("DataTable", fill="both", expand=True):
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
                fill="both",
                expand=True,
            )


# -- Progress & Meters --------------------------------------------------------


def _build_progress_page():
    slider_value = Signal(65.0)

    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Progress & Meters", font="heading-xl")
        bs.Label("Progress bars and gauges for showing values and status.", accent="secondary")

        with bs.GroupBox("Slider (drag to control progress bars)", fill="horizontal"):
            bs.Slider(min_value=0, max_value=100, signal=slider_value, fill="horizontal")

        with bs.GroupBox("ProgressBar", fill="horizontal", gap=8):
            bs.ProgressBar(signal=slider_value, max_value=100, fill="horizontal")
            bs.ProgressBar(value=75,  max_value=100, accent="success", fill="horizontal")
            bs.ProgressBar(value=45,  max_value=100, accent="danger",  fill="horizontal")
            bs.ProgressBar(value=30,  max_value=100, accent="warning", fill="horizontal")

        with bs.GroupBox("Gauge", fill="horizontal"):
            with bs.HStack(gap=16, anchor_items="center"):
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
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Layout", font="heading-xl")
        bs.Label("Containers, expandable panels, and split panes.", accent="secondary")

        with bs.GroupBox("Card", fill="horizontal", layout="hstack", fill_items="x", expand_items=True, gap=16):
            for title, body, color in [
                ("Users",   "1,234 active", "primary"),
                ("Revenue", "$45,678",       "success"),
                ("Errors",  "12 today",      "danger"),
            ]:
                with bs.Card(accent=color):
                    bs.Label(title, accent=color, font="body[bold]")
                    bs.Label(body, font="heading-lg")

        with bs.GroupBox("Accordion", fill="horizontal"):
            acc = bs.Accordion(fill="horizontal", accent="primary")
            with acc.add("Section 1", expanded=True):
                bs.Label("Content for section one.")
            with acc.add("Section 2"):
                bs.Label("Content for section two.")
            with acc.add("Section 3"):
                bs.Label("Content for section three.")

        with bs.GroupBox("SplitView", fill="both", expand=True):
            sv = bs.SplitView(orient="horizontal", fill="both", expand=True)
            with sv.add(padding=10, anchor_items="center"):
                bs.Label("Left Pane")
                bs.Label("Drag the sash to resize", accent="secondary", font="caption")
            with sv.add(padding=10, anchor_items="center"):
                bs.Label("Right Pane")
                bs.Label("Both panes are resizable", accent="secondary", font="caption")

        with bs.GroupBox("Separator", fill="horizontal", gap=8):
            bs.Separator(fill="horizontal")
            bs.Separator(accent="primary",  fill="horizontal")
            bs.Separator(accent="success",  fill="horizontal")
            bs.Separator(accent="danger",   fill="horizontal")


# -- Navigation ---------------------------------------------------------------


def _build_navigation_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Navigation", font="heading-xl")
        bs.Label("Tab-based navigation widgets.", accent="secondary")

        with bs.GroupBox("Tabs (horizontal)", fill="both", expand=True):
            tabs = bs.Tabs(fill="both", expand=True)
            with tabs.add("dashboard", label="Dashboard", icon="house"):
                bs.Label("Dashboard content goes here.", padding=20)
            with tabs.add("files", label="Files", icon="folder2"):
                bs.Label("Browse your files here.", padding=20)
            with tabs.add("settings", label="Settings", icon="gear"):
                bs.Label("Configure your settings.", padding=20)

        with bs.GroupBox("Tabs (closable + addable)", fill="both", expand=True):
            tabs2 = bs.Tabs(allow_close=True, allow_add=True, fill="both", expand=True)
            with tabs2.add("doc1", label="Document 1", icon="file-text"):
                bs.Label("Content for Document 1.", padding=20)


# -- Overlays -----------------------------------------------------------------


def _build_overlays_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Overlays", font="heading-xl")
        bs.Label("Toasts and tooltips.", accent="secondary")

        with bs.GroupBox("Tooltip", fill="horizontal"):
            bs.Label("Hover over the buttons below:")
            with bs.HStack(gap=8):
                b1 = bs.Button("Default",  accent="primary")
                b2 = bs.Button("Accented", accent="primary")
                b3 = bs.Button("Long tip", accent="default")
            bs.Tooltip(b1, "This is a basic tooltip.")
            bs.Tooltip(b2, "Tooltips can have accent colors.", accent="primary")
            bs.Tooltip(b3, "This is a longer tooltip that wraps. "
                           "It shows how tooltips handle multi-line content.",
                       wrap_width=200)

        with bs.GroupBox("Toast", fill="horizontal"):
            bs.Label("Click buttons to show toast notifications:")

            def show_toast(title, message, accent):
                bs.Toast(title=title, message=message, accent=accent, duration=3000).show()

            with bs.HStack(gap=8):
                bs.Button("Success", accent="success",
                          on_click=lambda: show_toast("Success", "Operation completed.", "success"))
                bs.Button("Warning", accent="warning",
                          on_click=lambda: show_toast("Warning", "Check your settings.", "warning"))
                bs.Button("Error",   accent="danger",
                          on_click=lambda: show_toast("Error", "Something went wrong.", "danger"))


# -- Dialogs ------------------------------------------------------------------


def _build_dialogs_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Dialogs", font="heading-xl")
        bs.Label("Click buttons to launch dialog types.", accent="secondary")

        with bs.GroupBox("Alert & Confirm", fill="horizontal"):
            with bs.HStack(gap=8):
                bs.Button("alert()",   on_click=lambda: bs.alert("Operation complete."))
                bs.Button("confirm()", accent="warning",
                          on_click=lambda: bs.Toast(
                              title="Result",
                              detail=f"confirm() → {bs.confirm('Continue?')}",
                              duration=2000,
                          ).show())

        with bs.GroupBox("Input Dialogs", fill="horizontal"):
            def _ask(fn, *args, **kw):
                result = fn(*args, **kw)
                if result is not None:
                    bs.Toast(title="Result", detail=str(result), duration=2000).show()

            with bs.HStack(gap=8):
                bs.Button("ask_string()",
                          on_click=lambda: _ask(bs.ask_string, "Enter your name:"))
                bs.Button("ask_integer()",
                          on_click=lambda: _ask(bs.ask_integer, "Enter age:", min_value=0, max_value=120))
                bs.Button("ask_date()",
                          on_click=lambda: _ask(bs.ask_date, title="Pick a date"))

        with bs.GroupBox("FormDialog", fill="horizontal"):
            def _show_form():
                dlg = bs.FormDialog(
                    title="Settings",
                    data={"name": "", "email": ""},
                    items=[
                        {"key": "name",  "label": "Name"},
                        {"key": "email", "label": "Email"},
                    ],
                )
                dlg.show()
                if dlg.result:
                    bs.Toast(title="Form Result", message=str(dlg.result), duration=3000).show()

            bs.Button("Open FormDialog", accent="primary", on_click=_show_form)


# -- Themes -------------------------------------------------------------------


def _build_theme_page():
    with bs.VStack(padding=20, gap=12, fill="both", expand=True, fill_items="horizontal"):
        bs.Label("Themes", font="heading-xl")
        bs.Label("Switch themes to see all widgets update in real time.", accent="secondary")

        with bs.GroupBox("Theme Selector", fill="horizontal", layout="grid", columns=2):
            style = bs.get_style()
            theme_names = sorted(s["name"] for s in style.theme_provider.list_themes())

            with bs.HStack(gap=8):
                bs.Label("Theme:", width=10)
                sel = bs.Select(options=theme_names, value=style.current_theme, fill="horizontal")
                sel.on_change(lambda e: sel._internal.after(0, lambda: bs.set_theme(sel.value)))

            with bs.HStack(gap=8):
                bs.Label("Quick:", width=10)
                bs.Button("Toggle Light / Dark", on_click=bs.toggle_theme)

        with bs.GroupBox("Accent Colors", fill="horizontal"):
            with bs.HStack(gap=4, fill="horizontal", fill_items="horizontal", expand_items=True):
                for color in ("primary", "secondary", "success", "warning", "danger"):
                    bs.Button(color.title(), accent=color)

        with bs.GroupBox("Surfaces", fill="horizontal"):
            with bs.HStack(gap=4, fill="horizontal", fill_items="horizontal", expand_items=True):
                for surface in ("chrome", "content", "card", "overlay", "input"):
                    with bs.VStack(padding=12, anchor_items="center", surface=surface):
                        bs.Label(surface.title(), surface=surface)


# =============================================================================
# Gallery app
# =============================================================================


def run_demo():
    """Run the bootstack widget gallery as an AppShell application."""
    with bs.AppShell(
        title="Widget Gallery",
        settings={"theme": "bootstrap-light"},
        size=(1100, 750),
    ) as shell:

        shell.toolbar.add_button(icon="sun", command=bs.toggle_theme)

        # Page registry: key → (page_frame, builder)
        _pages: dict[str, tuple[object, object]] = {}

        def _register(key, builder, *, text, icon, scrollable=False):
            page = shell.add_page(key, text=text, icon=icon, scrollable=scrollable)
            _pages[key] = (page, builder)

        _register("home",       _build_home_page,       text="Home",        icon="house")

        shell.add_separator()
        shell.add_header("Actions")
        _register("buttons",    _build_buttons_page,    text="Buttons",     icon="hand-index-thumb",   scrollable=True)

        shell.add_separator()
        shell.add_header("Inputs")
        _register("text-inputs",  _build_text_inputs_page,  text="Text Inputs",  icon="input-cursor-text", scrollable=True)
        _register("numeric",      _build_numeric_page,      text="Numeric & Date", icon="123",             scrollable=True)
        _register("forms",        _build_forms_page,        text="Forms",        icon="journal-text",      scrollable=True)
        _register("code-editor",  _build_code_editor_page,  text="Code Editor",  icon="code-slash",        scrollable=True)

        shell.add_separator()
        shell.add_header("Selection")
        _register("selection",  _build_selection_page,  text="Selection",   icon="ui-checks",          scrollable=True)
        _register("calendar",   _build_calendar_page,   text="Calendar",    icon="calendar3",          scrollable=True)

        shell.add_separator()
        shell.add_header("Data Display")
        _register("data",       _build_data_page,       text="Data Tables", icon="table",              scrollable=True)
        _register("progress",   _build_progress_page,   text="Progress",    icon="speedometer2",       scrollable=True)

        shell.add_separator()
        shell.add_header("Layout")
        _register("layout",     _build_layout_page,     text="Containers",  icon="layout-wtf",         scrollable=True)
        _register("navigation", _build_navigation_page, text="Tab Views",   icon="window-stack",       scrollable=True)

        shell.add_separator()
        shell.add_header("Overlays & Dialogs")
        _register("overlays",   _build_overlays_page,   text="Overlays",    icon="layers",             scrollable=True)
        _register("dialogs",    _build_dialogs_page,    text="Dialogs",     icon="chat-square-text",   scrollable=True)

        shell.add_separator()
        shell.add_header("Design System")
        _register("themes",     _build_theme_page,      text="Themes",      icon="palette",            scrollable=True)
        _register("typography", _build_typography_page, text="Typography",  icon="fonts",              scrollable=True)
        _register("icons",      _build_icons_page,      text="Icons",       icon="grid-3x3-gap",       scrollable=True)

        # Lazy-build: construct page content only on first visit
        _built: set[str] = set()

        def _build_page(key: str) -> None:
            if key in _built:
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

    shell.run()


def setup_demo(master):
    """Legacy entry point — the gallery now uses AppShell."""
    with bs.VStack(parent=master, fill="both", expand=True, padding=40):
        bs.Label(
            "Use 'bootstack gallery' to launch the Widget Gallery.",
            font="heading-lg",
        )