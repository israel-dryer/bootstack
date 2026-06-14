"""Static navigation building blocks shared by the shell's nav panel.

The standalone `SideNav` widget was retired with the AppShell rewrite; what
remains are the two non-interactive primitives the shell's `NavPanel` composes:

- SideNavHeader: a non-selectable section label
- SideNavSeparator: a visual divider between groups
"""

from bootstack.widgets._impl.composites.sidenav.header import SideNavHeader
from bootstack.widgets._impl.composites.sidenav.separator import SideNavSeparator

__all__ = [
    'SideNavHeader',
    'SideNavSeparator',
]
