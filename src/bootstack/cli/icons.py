"""Icons command — delegates to the ttkbootstrap-icons browser."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "icons",
        help="Browse Bootstrap Icons available in bootstack",
        description=(
            "Launch the Bootstrap Icons browser.\n\n"
            "Delegates to the ttkbootstrap-icons tool bundled with the "
            "ttkbootstrap_icons_bs package. Any icon name shown there can "
            "be used as the icon= parameter on any bootstack widget."
        ),
    )
    parser.set_defaults(func=lambda args: run_icons())


def run_icons() -> None:
    scripts = Path(sys.executable).parent
    name = "ttkbootstrap-icons.exe" if sys.platform == "win32" else "ttkbootstrap-icons"
    result = subprocess.run([str(scripts / name)])
    sys.exit(result.returncode)
