"""Internal composites for the clean-slate application shell.

Layered per `docs/_dev/appshell-navigation-spec.md`:

- `layout.ShellLayout` — Layer 1, the dumb region/slot band layout.
- `nav_panel.NavPanel` — the static single-select nav list (sidebar).
- `content_host.ContentHost` — context container for rendering detail bodies.
- `providers.NavProvider` / `StaticProvider` / `ListNavProvider` — Layer 3.
- `shell.Shell` — wires `NavModel` to the regions (single-tier path).

Later layers (rail, tree provider, collapse) build on top of these.
"""

from bootstack.widgets._impl.composites.shell.content_host import ContentHost
from bootstack.widgets._impl.composites.shell.layout import ShellLayout
from bootstack.widgets._impl.composites.shell.nav_panel import NavPanel
from bootstack.widgets._impl.composites.shell.providers import (
    ListNavProvider,
    NavProvider,
    StaticProvider,
)
from bootstack.widgets._impl.composites.shell.shell import Shell

__all__ = [
    "ShellLayout",
    "NavPanel",
    "ContentHost",
    "NavProvider",
    "StaticProvider",
    "ListNavProvider",
    "Shell",
]
