#!/usr/bin/env python
"""Generate API reference markdown files for bootstack.

Run this script before building docs with Zensical:
    python tools/gen_api_docs.py
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
REF_DIR = DOCS_DIR / "reference"

# API structure matching bootstack.api modules
API_MODULES = {
    "app": {
        "title": "App",
        "description": "Application, window management, and menus",
        "exports": {
            "App": "bootstack.runtime.app.App",
            "Window": "bootstack.runtime.app.App",  # Alias
            "Toplevel": "bootstack.runtime.toplevel.Toplevel",
            "get_current_app": "bootstack.runtime.app.get_current_app",
            "MenuManager": "bootstack.runtime.menu.MenuManager",
            "create_menu": "bootstack.runtime.menu.create_menu",
        },
    },
    "style": {
        "title": "Style",
        "description": "Theme and style management",
        "exports": {
            "Style": "bootstack.style.style.Style",
            "StyleResolver": "bootstack.style.style_resolver.StyleResolver",            "get_style": "bootstack.style.style.get_style",
            "get_style_builder": "bootstack.style.style.get_style_builder",
            "get_theme": "bootstack.style.style.get_theme",
            "get_theme_provider": "bootstack.style.style.get_theme_provider",
            "set_theme": "bootstack.style.style.set_theme",
            "toggle_theme": "bootstack.style.style.toggle_theme",
            "get_theme_color": "bootstack.style.style.get_theme_color",
            "get_themes": "bootstack.style.style.get_themes",
        },
    },
    "widgets": {
        "title": "Widgets",
        "description": "UI components",
        "exports": {
            # Primitives
            "Badge": "bootstack.widgets.primitives.badge.Badge",
            "Button": "bootstack.widgets.primitives.button.Button",
            "CheckButton": "bootstack.widgets.primitives.checkbutton.CheckButton",
            "CheckToggle": "bootstack.widgets.primitives.checktoggle.CheckToggle",
            "Combobox": "bootstack.widgets.primitives.combobox.Combobox",
            "Entry": "bootstack.widgets.primitives.entry.Entry",
            "Frame": "bootstack.widgets.primitives.frame.Frame",
            "Label": "bootstack.widgets.primitives.label.Label",
            "LabelFrame": "bootstack.widgets.primitives.labelframe.LabelFrame",
            "MenuButton": "bootstack.widgets.primitives.menubutton.MenuButton",
            "OptionMenu": "bootstack.widgets.primitives.optionmenu.OptionMenu",
            "PanedWindow": "bootstack.widgets.primitives.panedwindow.PanedWindow",
            "Progressbar": "bootstack.widgets.primitives.progressbar.Progressbar",
            "RadioButton": "bootstack.widgets.primitives.radiobutton.RadioButton",
            "RadioToggle": "bootstack.widgets.primitives.radiotoggle.RadioToggle",
            "Scale": "bootstack.widgets.primitives.scale.Scale",
            "Scrollbar": "bootstack.widgets.primitives.scrollbar.Scrollbar",
            "SelectBox": "bootstack.widgets.primitives.selectbox.SelectBox",
            "Separator": "bootstack.widgets.primitives.separator.Separator",
            "SizeGrip": "bootstack.widgets.primitives.sizegrip.SizeGrip",
            "Spinbox": "bootstack.widgets.primitives.spinbox.Spinbox",
            "TreeView": "bootstack.widgets.primitives.treeview.TreeView",
            # Composites
            "ButtonGroup": "bootstack.widgets.composites.buttongroup.ButtonGroup",
            "Calendar": "bootstack.widgets.composites.calendar.Calendar",
            "ContextMenu": "bootstack.widgets.composites.contextmenu.ContextMenu",
            "ContextMenuItem": "bootstack.widgets.composites.contextmenu.ContextMenuItem",
            "DateEntry": "bootstack.widgets.composites.dateentry.DateEntry",
            "DropdownButton": "bootstack.widgets.composites.dropdownbutton.DropdownButton",
            "Field": "bootstack.widgets.composites.field.Field",
            "FieldOptions": "bootstack.widgets.composites.field.FieldOptions",
            "Form": "bootstack.widgets.composites.form.Form",
            "LabeledScale": "bootstack.widgets.composites.labeledscale.LabeledScale",
            "Meter": "bootstack.widgets.composites.meter.Meter",
            "NumericEntry": "bootstack.widgets.composites.numericentry.NumericEntry",
            "PageStack": "bootstack.widgets.composites.pagestack.PageStack",
            "PasswordEntry": "bootstack.widgets.composites.passwordentry.PasswordEntry",
            "PathEntry": "bootstack.widgets.composites.pathentry.PathEntry",
            "RadioGroup": "bootstack.widgets.composites.radiogroup.RadioGroup",
            "ScrolledText": "bootstack.widgets.composites.scrolledtext.ScrolledText",
            "ScrollView": "bootstack.widgets.composites.scrollview.ScrollView",
            "SpinnerEntry": "bootstack.widgets.composites.spinnerentry.SpinnerEntry",
            "TableView": "bootstack.widgets.composites.tableview.TableView",
            "TextEntry": "bootstack.widgets.composites.textentry.TextEntry",
            "TimeEntry": "bootstack.widgets.composites.timeentry.TimeEntry",
            "Toast": "bootstack.widgets.composites.toast.Toast",
            "ToggleGroup": "bootstack.widgets.composites.togglegroup.ToggleGroup",
            "ToolTip": "bootstack.widgets.composites.tooltip.ToolTip",
        },
    },
    "dialogs": {
        "title": "Dialogs",
        "description": "Dialog windows for common interactions",
        "exports": {
            "Dialog": "bootstack.dialogs.dialog.Dialog",
            "DialogButton": "bootstack.dialogs.dialog.DialogButton",
            "FilterDialog": "bootstack.dialogs.filterdialog.FilterDialog",
            "FormDialog": "bootstack.dialogs.formdialog.FormDialog",
            "MessageDialog": "bootstack.dialogs.message.MessageDialog",
            "MessageBox": "bootstack.dialogs.message.MessageBox",
            "QueryDialog": "bootstack.dialogs.query.QueryDialog",
            "QueryBox": "bootstack.dialogs.query.QueryBox",
            "DateDialog": "bootstack.dialogs.datedialog.DateDialog",
            "FontDialog": "bootstack.dialogs.fontdialog.FontDialog",
            "ColorChooser": "bootstack.dialogs.colorchooser.ColorChooser",
            "ColorChooserDialog": "bootstack.dialogs.colorchooser.ColorChooserDialog",
        },
    },
    "data": {
        "title": "Data",
        "description": "Data sources for widgets",
        "exports": {
            "BaseDataSource": "bootstack.datasource.base.BaseDataSource",
            "MemoryDataSource": "bootstack.datasource.memory_source.MemoryDataSource",
            "SqliteDataSource": "bootstack.datasource.sqlite_source.SqliteDataSource",
            "FileDataSource": "bootstack.datasource.file_source.FileDataSource",
            "FileSourceConfig": "bootstack.datasource.file_source.FileSourceConfig",
            "DataSourceProtocol": "bootstack.datasource.types.DataSourceProtocol",
            "Record": "bootstack.datasource.types.Record",
            "Primitive": "bootstack.datasource.types.Primitive",
        },
    },
    "i18n": {
        "title": "i18n",
        "description": "Internationalization and localization",
        "exports": {
            "MessageCatalog": "bootstack.core.localization.msgcat.MessageCatalog",
            "L": "bootstack.core.localization.specs.L",
            "LV": "bootstack.core.localization.specs.LV",
            "IntlFormatter": "bootstack.core.localization.intl_format.IntlFormatter",
        },
    },
    "utils": {
        "title": "Utils",
        "description": "Core utilities for reactive programming and validation",
        "exports": {
            "Signal": "bootstack.core.signals.signal.Signal",
            "TraceOperation": "bootstack.core.signals.signal.TraceOperation",
            "ValidationRule": "bootstack.core.validation.ValidationRule",
            "ValidationResult": "bootstack.core.validation.ValidationResult",
            "SetVar": "bootstack.core.variables.SetVar",
        },
    },
}


def write_ref_page(path: Path, identifier: str, title: str):
    """Write a reference page for a single symbol."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"# {title}\n\n::: {identifier}\n"
    path.write_text(content, encoding="utf-8")
    print(f"  {path.relative_to(ROOT)}")


def write_module_index(module_name: str, module_info: dict):
    """Generate index page for a module."""
    module_dir = REF_DIR / module_name
    module_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {module_info['title']}",
        "",
        module_info['description'],
        "",
        "## Exports",
        "",
        "| Name | Description |",
        "|------|-------------|",
    ]

    for name in sorted(module_info['exports'].keys()):
        lines.append(f"| [{name}]({name}.md) | |")

    index_path = module_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {index_path.relative_to(ROOT)}")


def write_main_index():
    """Generate the main API reference index."""
    lines = [
        "# API Reference",
        "",
        "Auto-generated API documentation for bootstack.",
        "",
        "## Modules",
        "",
        "| Module | Description |",
        "|--------|-------------|",
    ]

    for module_name, module_info in API_MODULES.items():
        lines.append(f"| [{module_info['title']}]({module_name}/index.md) | {module_info['description']} |")

    lines.extend([
        "",
        "## Usage",
        "",
        "All exports are available from the top-level package:",
        "",
        "```python",
        "import bootstack as bs",
        "",
        "# App",
        "app = bs.App(title=\"My App\", theme=\"bootstrap-dark\")",
        "",
        "# Widgets",
        "button = bs.Button(text=\"Click\", accent=\"success\")",
        "",
        "# Style",
        "bs.set_theme(\"bootstrap-light\")",
        "",
        "# Localization",
        "from bootstack import L",
        "label = bs.Label(app, text=L(\"Hello\"))",
        "",
        "app.mainloop()",
        "```",
    ])

    index_path = REF_DIR / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {index_path.relative_to(ROOT)}")


def main():
    print("Generating API reference docs...")
    print()

    total = 0

    for module_name, module_info in API_MODULES.items():
        print(f"[{module_info['title']}]")
        module_dir = REF_DIR / module_name

        # Generate individual pages
        for name, identifier in sorted(module_info['exports'].items()):
            write_ref_page(module_dir / f"{name}.md", identifier, title=name)
            total += 1

        # Generate module index
        write_module_index(module_name, module_info)
        print()

    # Generate main index
    print("[Main Index]")
    write_main_index()

    print(f"\nGenerated {total} API reference pages across {len(API_MODULES)} modules.")


if __name__ == "__main__":
    main()