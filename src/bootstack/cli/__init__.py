"""CLI entry point for bootstack.

The bootstack CLI provides commands for:
- Creating new projects (start)
- Running applications (run)
- Building for distribution (build)
- Adding components (add)
- Listing resources (list)

Usage:
    bootstack start <appname>        Create a new project
    bootstack run [path]             Run the application
    bootstack promote --pyinstaller  Enable PyInstaller support
    bootstack build                  Build for distribution
    bootstack add page <ClassName>   Add a new page (AppShell)
    bootstack add view <ClassName>   Add a new view
    bootstack add dialog <ClassName> Add a new dialog
    bootstack add theme <name>       Add a custom theme
    bootstack add i18n               Add i18n support
    bootstack list themes            List available themes
    bootstack doctor                 Diagnose project and environment health
    bootstack gallery                 Launch the widget gallery
    bootstack icons                   Browse Bootstrap Icons
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from bootstack.cli import add, build, doctor, icons, list_cmd, promote, run, start
from bootstack.cli.demo import run_demo


def main(argv: Sequence[str] | None = None) -> None:
    """Dispatch CLI commands registered in bootstack."""
    parser = argparse.ArgumentParser(
        prog="bootstack",
        description="bootstack command line interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  bootstack start MyApp              Create a new project
  bootstack start MyApp --template appshell  Create an AppShell project
  bootstack start MyApp --theme superhero    Use a specific theme
  bootstack run                      Run the application
  bootstack promote --pyinstaller    Enable PyInstaller support
  bootstack build                    Build for distribution
  bootstack add view SettingsView    Add a new view
  bootstack list themes              List available themes
  bootstack doctor                   Diagnose project and environment health
  bootstack gallery                  Launch the widget gallery
  bootstack icons                    Browse Bootstrap Icons

For more information on a command:
  bootstack <command> --help
""",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=_get_version(),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print full tracebacks on error",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="<command>",
    )

    # Register commands
    start.add_parser(subparsers)
    run.add_parser(subparsers)
    promote.add_parser(subparsers)
    build.add_parser(subparsers)
    add.add_parser(subparsers)
    list_cmd.add_parser(subparsers)
    doctor.add_parser(subparsers)
    icons.add_parser(subparsers)

    # Gallery command
    gallery_parser = subparsers.add_parser(
        "gallery",
        help="Launch the widget gallery",
    )
    gallery_parser.set_defaults(func=lambda args: run_demo())

    # demo is kept as a backwards-compatible alias
    demo_parser = subparsers.add_parser(
        "demo",
        help=argparse.SUPPRESS,
    )
    demo_parser.set_defaults(func=lambda args: run_demo())

    # Parse arguments
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)

    if func is None:
        parser.print_help()
        sys.exit(0)

    # Execute command
    try:
        func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
    except Exception as e:
        if getattr(args, "verbose", False):
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
            print("(Run with --verbose for the full traceback.)")
        sys.exit(1)


def _get_version() -> str:
    """Get the bootstack version string."""
    try:
        import bootstack

        return f"bootstack {bootstack.__version__}"
    except Exception:
        return "bootstack (unknown version)"
