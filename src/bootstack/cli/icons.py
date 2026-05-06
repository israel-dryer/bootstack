"""Icons command — standalone Bootstrap Icons browser."""
from __future__ import annotations

import argparse


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "icons",
        help="Browse Bootstrap Icons available in bootstack",
        description=(
            "Launch a visual browser for Bootstrap Icons.\n\n"
            "Displays common icons, size variants, context examples, and "
            "accent-coloured variants. Any icon name shown here can be used "
            "as the icon= parameter on any bootstack widget."
        ),
    )
    parser.set_defaults(func=lambda args: run_icons())


def run_icons() -> None:
    import bootstack as bs
    from bootstack.cli.demo import _build_icons_page

    app = bs.App(title="bootstack — Icons", size=(920, 680))
    scroll = bs.ScrollView(app)
    scroll.pack(fill="both", expand=True)
    _build_icons_page(scroll)
    app.mainloop()
