"""Internal composites for the clean-slate application shell.

Layered per `docs/_dev/appshell-navigation-spec.md`:

- `layout.ShellLayout` — Layer 1, the dumb region/slot band layout.

Later layers (wiring to `NavModel`, providers, rail) build on top of this.
"""

from bootstack.widgets._impl.composites.shell.layout import ShellLayout

__all__ = ["ShellLayout"]
