"""Project templates for bootstack start command."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

ContainerType = Literal["grid", "pack"]
TemplateType = Literal["basic", "appshell"]
NavStyle = Literal["single", "grouped", "master-detail", "workspaces"]


# =============================================================================
# Main entry point template
# =============================================================================

MAIN_PY_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import bootstack as bs

from {module_name}.views.main_view import MainView


def main() -> None:
    """Application entry point."""
    with bs.App(
        title="{app_name}",
        theme="{theme}",
        size=(800, 600),
    ) as app:
        MainView()

    app.run()


if __name__ == "__main__":
    main()
'''


# =============================================================================
# View templates (GridFrame vs PackFrame)
# =============================================================================

MAIN_VIEW_GRID_TEMPLATE = '''\
"""Main application view."""

import bootstack as bs


class MainView:
    """Main application view using a grid layout."""

    def __init__(self, parent=None):
        with bs.Grid(
            parent=parent,
            columns=["auto", 1],
            gap=10,
            padding=20,
            sticky_items="ew",
            fill="both",
            expand=True,
        ) as self.root:
            self._build()

    def _build(self) -> None:
        bs.Label("Welcome to {app_name}", font="heading-lg", columnspan=2)
        bs.Label("Name:")
        self.name_field = bs.TextField()
        bs.Label("Email:")
        self.email_field = bs.TextField()
        bs.Button(
            "Get Started",
            accent="primary",
            on_click=self._on_submit,
            columnspan=2,
        )

    def _on_submit(self) -> None:
        print(f"Name: {{self.name_field.value}}, Email: {{self.email_field.value}}")
'''


MAIN_VIEW_PACK_TEMPLATE = '''\
"""Main application view."""

import bootstack as bs


class MainView:
    """Main application view using a vertical stack layout."""

    def __init__(self, parent=None):
        with bs.VStack(
            parent=parent,
            gap=10,
            padding=20,
            fill="both",
            expand=True,
        ) as self.root:
            self._build()

    def _build(self) -> None:
        bs.Label("Welcome to {app_name}", font="heading-lg")
        self.name_field = bs.TextField(label="Name:", fill="x")
        self.email_field = bs.TextField(label="Email:", fill="x")
        bs.Button("Get Started", accent="primary", on_click=self._on_submit)

    def _on_submit(self) -> None:
        print(f"Name: {{self.name_field.value}}, Email: {{self.email_field.value}}")
'''


# =============================================================================
# View/Dialog add templates
# =============================================================================

VIEW_GRID_TEMPLATE = '''\
"""
{class_name} view.
"""

import bootstack as bs


class {class_name}:
    """{class_name} view."""

    def __init__(self, parent=None):
        with bs.Grid(
            parent=parent,
            columns=["auto", 1],
            gap=10,
            padding=20,
            sticky_items="ew",
            fill="both",
            expand=True,
        ) as self.root:
            self._build()

    def _build(self) -> None:
        bs.Label("{class_name}", font="heading-lg", columnspan=2)
        # Add your widgets here
'''


VIEW_PACK_TEMPLATE = '''\
"""
{class_name} view.
"""

import bootstack as bs


class {class_name}:
    """{class_name} view."""

    def __init__(self, parent=None):
        with bs.VStack(
            parent=parent,
            gap=10,
            padding=20,
            fill="both",
            expand=True,
        ) as self.root:
            self._build()

    def _build(self) -> None:
        bs.Label("{class_name}", font="heading-lg")
        # Add your widgets here
'''


DIALOG_TEMPLATE = '''\
"""
{class_name} dialog.
"""

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton


class {class_name}:
    """A custom {class_name} dialog.

    Usage::

        result = {class_name}(parent=app).show()
        if result:
            ...
    """

    def __init__(self, parent=None):
        self._dialog = Dialog(
            title="{class_name}",
            content_builder=self._build,
            buttons=[
                DialogButton("Cancel", role="cancel"),
                DialogButton("OK", role="primary", result=True, default=True),
            ],
            min_size=(360, 200),
            parent=parent,
        )

    def _build(self, frame) -> None:
        """Fill the dialog body."""
        with bs.VStack(padding=20, gap=8, parent=frame):
            bs.Label("Dialog content goes here.")

    def show(self):
        """Show the dialog modally and return its result (None if cancelled)."""
        self._dialog.show()
        return self._dialog.result
'''


# =============================================================================
# Package init template
# =============================================================================

INIT_PY_TEMPLATE = '''\
"""{app_name} package."""

__version__ = "0.1.0"
'''


# =============================================================================
# README template
# =============================================================================

README_TEMPLATE = '''\
# {app_name}

A bootstack application.

## Getting Started

### Development

```bash
# Run the application
python -m {module_name}

# Or use the CLI
bootstack run
```

### Building for Distribution

```bash
# Promote to packaging-ready (adds PyInstaller support)
bootstack promote --pyinstaller

# Build the executable
bootstack build
```

## Project Structure

```
{project_dir}/
├── src/{module_name}/
│   ├── __init__.py
│   ├── main.py
│   └── views/
│       └── main_view.py
├── assets/
├── bootstack.toml
└── README.md
```

## Configuration

Application settings are defined in `bootstack.toml`:

- `[app]` - Application metadata
- `[layout]` - Default layout preferences
- `[build]` - Build/packaging configuration (after `bootstack promote`)
'''


# =============================================================================
# AppShell templates
# =============================================================================

def _appshell_chrome(app_name: str) -> str:
    """The shared menu bar, command bar, and status bar baseline for AppShell
    scaffolds. Delete what you do not need."""
    return f'''\
        # --- Menu bar -------------------------------------------------------
        with shell.menubar.add_menu("File") as file_menu:
            file_menu.add_action("Quit", shortcut="Mod+Q", on_click=shell.close)
        with shell.menubar.add_menu("Help") as help_menu:
            help_menu.add_action(
                "About",
                on_click=lambda: bs.alert("{app_name}", title="About"),
            )

        # --- Command bar ----------------------------------------------------
        shell.commandbar.add_theme_toggle()

        # --- Status bar -----------------------------------------------------
        shell.statusbar.add_text("Ready")
        shell.statusbar.add_text("v0.1.0", side="right")
'''


APPSHELL_MAIN_SINGLE_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import bootstack as bs

from {module_name}.pages.home_page import HomePage
from {module_name}.pages.settings_page import SettingsPage


def main() -> None:
    """Application entry point."""
    with bs.AppShell(
        title="{app_name}",
        theme="{theme}",
        size=(1000, 650),
        show_statusbar=True,
    ) as shell:
{chrome}
        # --- Navigation: a flat sidebar of pages ----------------------------
        with shell.add_page("home", text="Home", icon="house"):
            HomePage()

        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            SettingsPage()

        shell.navigate("home")

    shell.run()


if __name__ == "__main__":
    main()
'''


APPSHELL_MAIN_GROUPED_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import bootstack as bs

from {module_name}.pages.home_page import HomePage
from {module_name}.pages.reports_page import ReportsPage
from {module_name}.pages.profile_page import ProfilePage
from {module_name}.pages.settings_page import SettingsPage


def main() -> None:
    """Application entry point."""
    with bs.AppShell(
        title="{app_name}",
        theme="{theme}",
        size=(1000, 650),
        show_statusbar=True,
    ) as shell:
{chrome}
        # --- Navigation: pages grouped under section headers ----------------
        shell.add_header("Workspace")
        with shell.add_page("home", text="Home", icon="house"):
            HomePage()
        with shell.add_page("reports", text="Reports", icon="bar-chart"):
            ReportsPage()

        shell.add_header("Account")
        with shell.add_page("profile", text="Profile", icon="person"):
            ProfilePage()

        with shell.add_footer_page("settings", text="Settings", icon="gear"):
            SettingsPage()

        shell.navigate("home")

    shell.run()


if __name__ == "__main__":
    main()
'''


APPSHELL_MAIN_MASTER_DETAIL_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import bootstack as bs
from bootstack.data import MemoryDataSource

from {module_name}.pages.detail_view import DetailView

# Sample records drive the sidebar list. Swap in your own data source.
RECORDS = MemoryDataSource().load([
    {{"id": 1, "title": "Dana Reyes", "text": "Q3 roadmap review", "icon": "person"}},
    {{"id": 2, "title": "Sam Okonkwo", "text": "Budget approval", "icon": "person"}},
    {{"id": 3, "title": "Priya Nair", "text": "New hire onboarding", "icon": "person"}},
])


def main() -> None:
    """Application entry point."""
    with bs.AppShell(
        title="{app_name}",
        theme="{theme}",
        size=(1000, 650),
        show_statusbar=True,
    ) as shell:
{chrome}
        # --- Navigation: a record list drives a detail view -----------------
        shell.list_nav(RECORDS)

        @shell.detail
        def show(record):
            DetailView(record)

    shell.run()


if __name__ == "__main__":
    main()
'''


APPSHELL_MAIN_WORKSPACES_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import bootstack as bs

from {module_name}.pages.home_page import HomePage
from {module_name}.pages.reports_page import ReportsPage
from {module_name}.pages.settings_page import SettingsPage


def main() -> None:
    """Application entry point."""
    with bs.AppShell(
        title="{app_name}",
        theme="{theme}",
        size=(1000, 650),
        show_statusbar=True,
        rail_labels=True,
    ) as shell:
{chrome}
        # --- Navigation: a labeled rail of workspaces -----------------------
        with shell.add_workspace("home", text="Home", icon="house") as ws:
            with ws.add_page("overview", text="Overview", icon="speedometer2"):
                HomePage()

        with shell.add_workspace("reports", text="Reports", icon="bar-chart") as ws:
            with ws.add_page("monthly", text="Monthly", icon="calendar3"):
                ReportsPage()

        with shell.add_footer_workspace("settings", text="Settings", icon="gear") as ws:
            with ws.add_page("general", text="General", icon="sliders"):
                SettingsPage()

    shell.run()


if __name__ == "__main__":
    main()
'''


APPSHELL_HOME_PAGE_TEMPLATE = '''\
"""Home page."""

import bootstack as bs


class HomePage:
    """Home page content."""

    def __init__(self, parent=None):
        with bs.VStack(parent=parent, padding=20, gap=12, fill="both", expand=True) as self.root:
            self._build()

    def _build(self):
        bs.Label("Welcome to {app_name}", font="heading-xl")
        bs.Label(
            "This is your home page. Edit this file to get started.",
            wrap_width=500,
        )
        with bs.GroupBox("Getting Started", fill="both", expand=True):
            bs.Label(
                "Add your widgets here.\\n\\n"
                "To add another page:\\n"
                "  1. Run \\'bootstack add page <Name>\\' to generate the file.\\n"
                "  2. In main.py, add a \\'with shell.add_page(...):\\' block\\n"
                "     and instantiate your page class inside it."
            )
'''


APPSHELL_SETTINGS_PAGE_TEMPLATE = '''\
"""Settings page."""

import bootstack as bs


class SettingsPage:
    """Settings page content."""

    def __init__(self, parent=None):
        with bs.VStack(parent=parent, padding=20, gap=12, fill="both", expand=True) as self.root:
            self._build()

    def _build(self):
        bs.Label("Settings", font="heading-xl[bold]")
        bs.Label("Configure your application preferences.", wrap_width=500)
        with bs.GroupBox("Preferences", fill="both", expand=True):
            with bs.HStack(gap=8):
                bs.Label("Theme:")
                bs.ThemeToggle()
'''


APPSHELL_PAGE_TEMPLATE = '''\
"""{page_title} page."""

import bootstack as bs


class {class_name}:
    """{page_title} page content."""

    def __init__(self, parent=None):
        with bs.VStack(parent=parent, padding=20, gap=12, fill="both", expand=True) as self.root:
            self._build()

    def _build(self):
        bs.Label("{page_title}", font="heading-lg")
        with bs.GroupBox("Content", fill="both", expand=True):
            pass  # Add your widgets here
'''


APPSHELL_CONTENT_PAGE_TEMPLATE = '''\
"""{page_title} page."""

import bootstack as bs


class {class_name}:
    """{page_title} page content."""

    def __init__(self, parent=None):
        with bs.VStack(parent=parent, padding=20, gap=12, fill="both", expand=True) as self.root:
            self._build()

    def _build(self):
        bs.Label("{page_title}", font="heading-lg")
        with bs.GroupBox("Content", fill="both", expand=True):
            bs.Label("Add your widgets here.")
'''


APPSHELL_DETAIL_VIEW_TEMPLATE = '''\
"""Detail view for the record selected in the sidebar list."""

import bootstack as bs


class DetailView:
    """Renders the record selected in the master list."""

    def __init__(self, record, parent=None):
        self.record = record
        with bs.VStack(parent=parent, padding=20, gap=12, fill="both", expand=True) as self.root:
            self._build()

    def _build(self):
        bs.Label(self.record["title"], font="heading-lg")
        bs.Label(self.record.get("text", ""), accent="secondary")
        bs.Separator(fill="x")
        bs.Label("Detail content for this record goes here.")
'''


APPSHELL_README_TEMPLATE = '''\
# {app_name}

A bootstack application using AppShell navigation.

## Getting Started

### Development

```bash
# Run the application
python -m {module_name}

# Or use the CLI
bootstack run
```

### Adding Pages

```bash
# Scaffold a new page
bootstack add page DashboardPage

# Then wire it up in main.py:
#   from {module_name}.pages.dashboard_page import DashboardPage
#   with shell.add_page("dashboard", text="Dashboard", icon="speedometer2"):
#       DashboardPage()
```

### Building for Distribution

```bash
# Promote to packaging-ready (adds PyInstaller support)
bootstack promote --pyinstaller

# Build the executable
bootstack build
```

## Project Structure

```
{project_dir}/
\u251c\u2500\u2500 src/{module_name}/
\u2502   \u251c\u2500\u2500 __init__.py
\u2502   \u251c\u2500\u2500 main.py
\u2502   \u2514\u2500\u2500 pages/
\u2502       \u251c\u2500\u2500 __init__.py
\u2502       \u251c\u2500\u2500 home_page.py
\u2502       \u2514\u2500\u2500 settings_page.py
\u251c\u2500\u2500 assets/
\u251c\u2500\u2500 bootstack.toml
\u2514\u2500\u2500 README.md
```

## Configuration

Application settings are defined in `bootstack.toml`:

- `[app]` - Application metadata
- `[layout]` - Default layout preferences
- `[build]` - Build/packaging configuration (after `bootstack promote`)
'''


def create_page(
    class_name: str,
    target_dir: Path,
    scrollable: bool = False,
) -> Path:
    """Create a new AppShell page file.

    Args:
        class_name: Page class name (CamelCase).
        target_dir: Directory to create the page in.
        scrollable: If True, the page template notes that
            `scrollable=True` should be passed to `add_page()`.

    Returns:
        Path to the created file.
    """
    file_name = _camel_to_snake(class_name) + ".py"

    # Derive a readable title from the class name (e.g. "DashboardPage" -> "Dashboard")
    page_title = class_name
    if page_title.endswith("Page"):
        page_title = page_title[:-4]
    # Insert spaces before uppercase letters
    import re
    page_title = re.sub(r"([a-z])([A-Z])", r"\1 \2", page_title)

    content = APPSHELL_PAGE_TEMPLATE.format(
        class_name=class_name,
        page_title=page_title,
    )

    file_path = target_dir / file_name
    file_path.write_text(content, encoding="utf-8")

    return file_path


def create_project(
    name: str,
    target_dir: Path,
    container: ContainerType = "grid",
    theme: str = "bootstrap-light",
    template: TemplateType = "basic",
    simple: bool = False,
    nav: NavStyle = "single",
) -> None:
    """Create a new bootstack project.

    Args:
        name: Application name.
        target_dir: Target directory for the project.
        container: Default container type ('grid' or 'pack').
        theme: Theme name for the application.
        template: Project template ('basic' or 'appshell').
        simple: If True, create minimal project without build config.
        nav: Navigation style for the appshell template ('single', 'grouped',
            'master-detail', or 'workspaces'). Ignored for the basic template.
    """
    if template == "appshell":
        _create_appshell_project(name, target_dir, theme, simple, nav)
    else:
        _create_basic_project(name, target_dir, container, theme, simple)


def _create_basic_project(
    name: str,
    target_dir: Path,
    container: ContainerType,
    theme: str,
    simple: bool,
) -> None:
    """Create a basic single-view project."""
    from bootstack.cli.config import write_config

    # Normalize names
    name_lower = name.lower().replace(" ", "_").replace("-", "_")
    module_name = name_lower

    # Create directory structure
    src_dir = target_dir / "src" / module_name
    views_dir = src_dir / "views"
    assets_dir = target_dir / "assets"

    src_dir.mkdir(parents=True, exist_ok=True)
    views_dir.mkdir(parents=True, exist_ok=True)
    if not simple:
        assets_dir.mkdir(parents=True, exist_ok=True)

    # Write main.py
    main_content = MAIN_PY_TEMPLATE.format(
        app_name=name,
        module_name=module_name,
        theme=theme,
    )
    (src_dir / "main.py").write_text(main_content, encoding="utf-8")

    # Write __init__.py
    init_content = INIT_PY_TEMPLATE.format(app_name=name)
    (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # Write views/__init__.py
    (views_dir / "__init__.py").write_text(
        '"""Views package."""\n', encoding="utf-8"
    )

    # Write main_view.py
    if container == "grid":
        view_template = MAIN_VIEW_GRID_TEMPLATE
    else:
        view_template = MAIN_VIEW_PACK_TEMPLATE

    view_content = view_template.format(app_name=name)
    (views_dir / "main_view.py").write_text(view_content, encoding="utf-8")

    # Write bootstack.toml
    write_config(
        path=target_dir / "bootstack.toml",
        name=name,
        entry=f"src/{module_name}/main.py",
        theme=theme,
        template="basic",
        include_build=False,
    )

    # Write README.md
    if not simple:
        readme_content = README_TEMPLATE.format(
            app_name=name,
            module_name=module_name,
            project_dir=target_dir.name,
        )
        (target_dir / "README.md").write_text(readme_content, encoding="utf-8")


_APPSHELL_MAIN_TEMPLATES = {
    "single": APPSHELL_MAIN_SINGLE_TEMPLATE,
    "grouped": APPSHELL_MAIN_GROUPED_TEMPLATE,
    "master-detail": APPSHELL_MAIN_MASTER_DETAIL_TEMPLATE,
    "workspaces": APPSHELL_MAIN_WORKSPACES_TEMPLATE,
}


def _create_appshell_project(
    name: str,
    target_dir: Path,
    theme: str,
    simple: bool,
    nav: NavStyle = "single",
) -> None:
    """Create an AppShell project with the chosen navigation style."""
    from bootstack.cli.config import write_config

    # Normalize names
    name_lower = name.lower().replace(" ", "_").replace("-", "_")
    module_name = name_lower

    # Create directory structure
    src_dir = target_dir / "src" / module_name
    pages_dir = src_dir / "pages"
    assets_dir = target_dir / "assets"

    src_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)
    if not simple:
        assets_dir.mkdir(parents=True, exist_ok=True)

    # Write main.py for the chosen navigation style
    main_template = _APPSHELL_MAIN_TEMPLATES.get(nav, APPSHELL_MAIN_SINGLE_TEMPLATE)
    main_content = main_template.format(
        app_name=name,
        module_name=module_name,
        theme=theme,
        chrome=_appshell_chrome(name),
    )
    (src_dir / "main.py").write_text(main_content, encoding="utf-8")

    # Write __init__.py
    init_content = INIT_PY_TEMPLATE.format(app_name=name)
    (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # Write pages/__init__.py
    (pages_dir / "__init__.py").write_text(
        '"""Pages package."""\n', encoding="utf-8"
    )

    def _write_content_page(class_name: str, title: str) -> None:
        content = APPSHELL_CONTENT_PAGE_TEMPLATE.format(
            class_name=class_name, page_title=title
        )
        (pages_dir / f"{_camel_to_snake(class_name)}.py").write_text(
            content, encoding="utf-8"
        )

    # Write the page files the chosen nav style imports
    if nav == "master-detail":
        (pages_dir / "detail_view.py").write_text(
            APPSHELL_DETAIL_VIEW_TEMPLATE, encoding="utf-8"
        )
    else:
        (pages_dir / "home_page.py").write_text(
            APPSHELL_HOME_PAGE_TEMPLATE.format(app_name=name), encoding="utf-8"
        )
        (pages_dir / "settings_page.py").write_text(
            APPSHELL_SETTINGS_PAGE_TEMPLATE, encoding="utf-8"
        )
        if nav in ("grouped", "workspaces"):
            _write_content_page("ReportsPage", "Reports")
        if nav == "grouped":
            _write_content_page("ProfilePage", "Profile")

    # Write bootstack.toml
    write_config(
        path=target_dir / "bootstack.toml",
        name=name,
        entry=f"src/{module_name}/main.py",
        theme=theme,
        template="appshell",
        include_build=False,
    )

    # Write README.md
    if not simple:
        readme_content = APPSHELL_README_TEMPLATE.format(
            app_name=name,
            module_name=module_name,
            project_dir=target_dir.name,
        )
        (target_dir / "README.md").write_text(readme_content, encoding="utf-8")


def create_view(
    class_name: str,
    target_dir: Path,
    container: ContainerType = "grid",
) -> Path:
    """Create a new view file.

    Args:
        class_name: View class name (CamelCase).
        target_dir: Directory to create the view in.
        container: Container type ('grid' or 'pack').

    Returns:
        Path to the created file.
    """
    # Convert CamelCase to snake_case
    file_name = _camel_to_snake(class_name) + ".py"

    if container == "grid":
        template = VIEW_GRID_TEMPLATE
    else:
        template = VIEW_PACK_TEMPLATE

    content = template.format(class_name=class_name)

    file_path = target_dir / file_name
    file_path.write_text(content, encoding="utf-8")

    return file_path


def create_dialog(
    class_name: str,
    target_dir: Path,
) -> Path:
    """Create a new dialog file.

    Args:
        class_name: Dialog class name (CamelCase).
        target_dir: Directory to create the dialog in.

    Returns:
        Path to the created file.
    """
    file_name = _camel_to_snake(class_name) + ".py"
    content = DIALOG_TEMPLATE.format(class_name=class_name)

    file_path = target_dir / file_name
    file_path.write_text(content, encoding="utf-8")

    return file_path


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    import re

    # Insert underscore before uppercase letters and lowercase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
