"""Project templates for bootstack start command."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

ContainerType = Literal["grid", "pack"]
TemplateType = Literal["basic", "appshell"]


# =============================================================================
# Main entry point template
# =============================================================================

MAIN_PY_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import os

import bootstack as bs

from {module_name}.views.main_view import MainView


def main() -> None:
    """Application entry point."""
    with bs.App(
        title="{app_name}",
        settings={{"theme": os.environ.get("BOOTSTACK_THEME", "{theme}")}},
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
        bs.Label("Welcome to {app_name}", font="heading-lg[bold]", columnspan=2)
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
        bs.Label("Welcome to {app_name}", font="heading-lg[bold]")
        self.name_field = bs.TextField(label="Name:", fill="horizontal")
        self.email_field = bs.TextField(label="Email:", fill="horizontal")
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
        bs.Label("{class_name}", font="heading-lg[bold]", columnspan=2)
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
        bs.Label("{class_name}", font="heading-lg[bold]")
        # Add your widgets here
'''


DIALOG_TEMPLATE = '''\
"""
{class_name} dialog.
"""

import bootstack as bs
from bootstack.dialogs import Dialog


class {class_name}(Dialog):
    """{class_name} modal dialog."""

    def __init__(self, parent, title: str = "{class_name}", **kwargs):
        super().__init__(parent, title=title, **kwargs)

    def create_body(self, master) -> bs.Frame:
        """Create the dialog body."""
        body = bs.Frame(master, padding=20)

        bs.Label(
            body,
            text="Dialog content goes here",
        ).pack(pady=10)

        return body

    def create_buttonbox(self, master) -> bs.Frame:
        """Create the dialog buttons."""
        box = bs.Frame(master, padding=(20, 10))

        bs.Button(
            box,
            text="Cancel",
            command=self.cancel,
        ).pack(side="right", padx=5)

        bs.Button(
            box,
            text="OK",
            accent="primary",
            command=self.ok,
        ).pack(side="right")

        return box

    def validate(self) -> bool:
        """Validate dialog input before closing."""
        return True

    def apply(self) -> None:
        """Process dialog input after OK is clicked."""
        self.result = True
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
- `[settings]` - Runtime settings (theme, language)
- `[layout]` - Default layout preferences
- `[build]` - Build/packaging configuration (after `bootstack promote`)
'''


# =============================================================================
# AppShell templates
# =============================================================================

APPSHELL_MAIN_PY_TEMPLATE = '''\
"""
{app_name} - A bootstack application.

Run with: python -m {module_name}
"""

import os

import bootstack as bs

from {module_name}.pages.home_page import HomePage
from {module_name}.pages.settings_page import SettingsPage


def main() -> None:
    """Application entry point."""
    with bs.AppShell(
        title="{app_name}",
        settings={{"theme": os.environ.get("BOOTSTACK_THEME", "{theme}")}},
        size=(1000, 650),
    ) as shell:
        shell.toolbar.add_button(icon="sun", on_click=bs.toggle_theme)

        with shell.add_page("home", text="Home", icon="house"):
            HomePage()

        shell.add_separator()

        with shell.add_page("settings", text="Settings", icon="gear", is_footer=True):
            SettingsPage()

        shell.navigate("home")

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
        bs.Label("Welcome to {app_name}", font="heading-xl[bold]")
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
                bs.Button("Toggle Light / Dark", on_click=bs.toggle_theme)
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
        bs.Label("{page_title}", font="heading-xl[bold]")
        with bs.GroupBox("Content", fill="both", expand=True):
            pass  # Add your widgets here
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
#   page = shell.add_page("dashboard", text="Dashboard", icon="speedometer2")
#   DashboardPage(page)
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
- `[settings]` - Runtime settings (theme, language)
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
) -> None:
    """Create a new bootstack project.

    Args:
        name: Application name.
        target_dir: Target directory for the project.
        container: Default container type ('grid' or 'pack').
        theme: Theme name for the application.
        template: Project template ('basic' or 'appshell').
        simple: If True, create minimal project without build config.
    """
    if template == "appshell":
        _create_appshell_project(name, target_dir, theme, simple)
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


def _create_appshell_project(
    name: str,
    target_dir: Path,
    theme: str,
    simple: bool,
) -> None:
    """Create an AppShell project with sidebar navigation and pages."""
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

    # Write main.py
    main_content = APPSHELL_MAIN_PY_TEMPLATE.format(
        app_name=name,
        module_name=module_name,
        theme=theme,
    )
    (src_dir / "main.py").write_text(main_content, encoding="utf-8")

    # Write __init__.py
    init_content = INIT_PY_TEMPLATE.format(app_name=name)
    (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")

    # Write pages/__init__.py
    (pages_dir / "__init__.py").write_text(
        '"""Pages package."""\n', encoding="utf-8"
    )

    # Write home_page.py
    home_content = APPSHELL_HOME_PAGE_TEMPLATE.format(app_name=name)
    (pages_dir / "home_page.py").write_text(home_content, encoding="utf-8")

    # Write settings_page.py
    (pages_dir / "settings_page.py").write_text(
        APPSHELL_SETTINGS_PAGE_TEMPLATE, encoding="utf-8"
    )

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
