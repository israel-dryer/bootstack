"""bootstack add command - Add views, dialogs, and i18n to a project."""

from __future__ import annotations

import argparse
from pathlib import Path

from bootstack.cli.config import TtkbConfig, find_config
from bootstack.cli.templates import create_dialog, create_page, create_view


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'add' subcommand parser."""
    parser = subparsers.add_parser(
        "add",
        help="Add components to the project",
        description="Add views, pages, dialogs, or i18n support to the project.",
    )
    add_subparsers = parser.add_subparsers(dest="component")

    # bootstack add page <ClassName>
    page_parser = add_subparsers.add_parser(
        "page",
        help="Add a new page (for AppShell projects)",
    )
    page_parser.add_argument(
        "class_name",
        help="Page class name (CamelCase, e.g., 'DashboardPage')",
    )
    page_parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Target directory (default: src/<app>/pages/)",
    )
    page_parser.add_argument(
        "--scrollable",
        action="store_true",
        help="Make the page scrollable (wraps content in a ScrollView)",
    )
    page_parser.set_defaults(func=run_add_page)

    # bootstack add view <ClassName>
    view_parser = add_subparsers.add_parser(
        "view",
        help="Add a new view",
    )
    view_parser.add_argument(
        "class_name",
        help="View class name (CamelCase, e.g., 'SettingsView')",
    )
    view_parser.add_argument(
        "--container",
        choices=["grid", "pack"],
        default=None,
        help="Container type (default: from bootstack.toml or 'grid')",
    )
    view_parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Target directory (default: src/<app>/views/)",
    )
    view_parser.set_defaults(func=run_add_view)

    # bootstack add dialog <ClassName>
    dialog_parser = add_subparsers.add_parser(
        "dialog",
        help="Add a new dialog",
    )
    dialog_parser.add_argument(
        "class_name",
        help="Dialog class name (CamelCase, e.g., 'ConfirmDialog')",
    )
    dialog_parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Target directory (default: src/<app>/dialogs/)",
    )
    dialog_parser.set_defaults(func=run_add_dialog)

    # bootstack add i18n
    i18n_parser = add_subparsers.add_parser(
        "i18n",
        help="Add internationalization support",
    )
    i18n_parser.add_argument(
        "--languages",
        nargs="+",
        default=["en"],
        help="Languages to support (default: en)",
    )
    i18n_parser.set_defaults(func=run_add_i18n)

    parser.set_defaults(func=lambda args: parser.print_help())


def run_add_view(args: argparse.Namespace) -> None:
    """Add a new view to the project."""
    class_name = args.class_name

    # Validate class name
    if not class_name[0].isupper():
        print("Error: Class name should be CamelCase (e.g., 'SettingsView')")
        return

    # Find project configuration
    config_path = find_config()
    if config_path is None:
        print("Error: No bootstack.toml found. Are you in a bootstack project?")
        return

    project_root = config_path.parent
    config = TtkbConfig.load(config_path)

    # Reject in AppShell projects — views belong to the basic template
    if config.app.template == "appshell":
        print("Error: 'bootstack add view' is for basic-template projects.")
        print("This project uses the 'appshell' template. Use 'bootstack add page' instead.")
        return

    # Determine container type
    container = args.container
    if container is None:
        container = config.layout.default_container

    # Determine target directory
    if args.dir:
        target_dir = args.dir
    else:
        # Parse entry point to find source directory
        entry_path = Path(config.app.entry)
        if entry_path.parts[0] == "src" and len(entry_path.parts) >= 2:
            module_name = entry_path.parts[1]
            target_dir = project_root / "src" / module_name / "views"
        else:
            target_dir = project_root / "views"

    target_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Views package."""\n', encoding="utf-8")

    # Create view
    file_path = create_view(class_name, target_dir, container)

    print(f"Created view: {file_path.relative_to(project_root)}")


def run_add_page(args: argparse.Namespace) -> None:
    """Add a new page to an AppShell project."""
    class_name = args.class_name

    # Validate class name
    if not class_name[0].isupper():
        print("Error: Class name should be CamelCase (e.g., 'DashboardPage')")
        return

    # Find project configuration
    config_path = find_config()
    if config_path is None:
        print("Error: No bootstack.toml found. Are you in a bootstack project?")
        return

    project_root = config_path.parent
    config = TtkbConfig.load(config_path)

    # Check that this is an AppShell project
    if config.app.template != "appshell":
        print("Error: 'bootstack add page' is for AppShell projects.")
        print("This project uses the 'basic' template. Use 'bootstack add view' instead.")
        return

    # Determine target directory and module name for the import hint
    entry_path = Path(config.app.entry)
    if entry_path.parts[0] == "src" and len(entry_path.parts) >= 2:
        module_name = entry_path.parts[1]
        default_target = project_root / "src" / module_name / "pages"
    else:
        module_name = None
        default_target = project_root / "pages"

    target_dir = args.dir if args.dir else default_target

    target_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Pages package."""\n', encoding="utf-8")

    # Create page
    scrollable = args.scrollable
    file_path = create_page(class_name, target_dir, scrollable=scrollable)

    print(f"Created page: {file_path.relative_to(project_root)}")
    print()
    print("This created the file only — it is NOT yet shown in the sidebar.")
    print("To register it with the AppShell, paste these lines into main.py:")
    print()
    import_module = f"{module_name}.pages" if module_name else "<module>.pages"
    print(f"  from {import_module}.{file_path.stem} import {class_name}")
    scrollable_arg = ", scrollable=True" if scrollable else ""
    print(f'  with shell.add_page("<id>", text="<Label>", icon="<icon>"{scrollable_arg}):')
    print(f"      {class_name}()")


def run_add_dialog(args: argparse.Namespace) -> None:
    """Add a new dialog to the project."""
    class_name = args.class_name

    # Validate class name
    if not class_name[0].isupper():
        print("Error: Class name should be CamelCase (e.g., 'ConfirmDialog')")
        return

    # Find project configuration
    config_path = find_config()
    if config_path is None:
        print("Error: No bootstack.toml found. Are you in a bootstack project?")
        return

    project_root = config_path.parent
    config = TtkbConfig.load(config_path)

    # Determine target directory
    if args.dir:
        target_dir = args.dir
    else:
        # Parse entry point to find source directory
        entry_path = Path(config.app.entry)
        if entry_path.parts[0] == "src" and len(entry_path.parts) >= 2:
            module_name = entry_path.parts[1]
            target_dir = project_root / "src" / module_name / "dialogs"
        else:
            target_dir = project_root / "dialogs"

    target_dir.mkdir(parents=True, exist_ok=True)

    # Ensure __init__.py exists
    init_file = target_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Dialogs package."""\n', encoding="utf-8")

    # Create dialog
    file_path = create_dialog(class_name, target_dir)

    print(f"Created dialog: {file_path.relative_to(project_root)}")


def run_add_i18n(args: argparse.Namespace) -> None:
    """Add internationalization support to the project."""
    languages = args.languages

    # Find project configuration
    config_path = find_config()
    if config_path is None:
        print("Error: No bootstack.toml found. Are you in a bootstack project?")
        return

    project_root = config_path.parent

    # Create locales directory structure
    locales_dir = project_root / "locales"

    for lang in languages:
        lang_dir = locales_dir / lang / "LC_MESSAGES"
        lang_dir.mkdir(parents=True, exist_ok=True)

        # Create .po file template
        po_file = lang_dir / "messages.po"
        if not po_file.exists():
            po_content = _get_po_template(lang)
            po_file.write_text(po_content, encoding="utf-8")
            print(f"Created: {po_file.relative_to(project_root)}")

    print()
    print("Internationalization support added!")
    print()
    print("Next steps:")
    print("  1. Add translatable strings to your .po files")
    print("  2. Compile with: msgfmt locales/<lang>/LC_MESSAGES/messages.po -o locales/<lang>/LC_MESSAGES/messages.mo")
    print("  3. Use translations in code: bs.L('Hello')")


def _get_po_template(lang: str) -> str:
    """Get a .po file template."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M%z")

    return f'''\
# {lang.upper()} translations for the application.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
#
msgid ""
msgstr ""
"Project-Id-Version: 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {now}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: {lang.upper()} <LL@li.org>\\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

# Example translation
# msgid "Hello"
# msgstr "Hello"
'''
