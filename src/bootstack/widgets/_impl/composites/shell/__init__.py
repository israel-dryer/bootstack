"""Internal composites for the clean-slate application shell.

Layered per `docs/_dev/appshell-navigation-spec.md`:

- `layout.ShellLayout` — Layer 1, the dumb region/slot band layout.
- `nav_panel.NavPanel` — the static single-select nav list (sidebar).
- `providers.NavProvider` / `StaticProvider` — Layer 3, what fills a workspace.
- `shell.Shell` — wires `NavModel` to the regions (single-tier path).

Later layers (rail, data-bound providers, collapse) build on top of these.
"""

from bootstack.widgets._impl.composites.shell.layout import ShellLayout
from bootstack.widgets._impl.composites.shell.nav_panel import NavPanel
from bootstack.widgets._impl.composites.shell.providers import NavProvider, StaticProvider
from bootstack.widgets._impl.composites.shell.shell import Shell

__all__ = ["ShellLayout", "NavPanel", "NavProvider", "StaticProvider", "Shell"]
