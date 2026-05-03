"""SideNav widgets for building navigation interfaces.

This package provides a complete navigation solution:

- SideNav: Main container with pane, header, content, and footer
- SideNavGroup: Collapsible group of items (expander in expanded mode, popup in compact)
- SideNavItem: Selectable navigation item with icon and text
- SideNavHeader: Non-selectable section label
- SideNavSeparator: Visual divider between groups
"""

from bootstack.widgets.composites.sidenav.item import SideNavItem
from bootstack.widgets.composites.sidenav.group import SideNavGroup
from bootstack.widgets.composites.sidenav.header import SideNavHeader
from bootstack.widgets.composites.sidenav.separator import SideNavSeparator
from bootstack.widgets.composites.sidenav.view import SideNav

# Backward compatibility aliases
NavigationView = SideNav
NavigationViewItem = SideNavItem
NavigationViewGroup = SideNavGroup
NavigationViewHeader = SideNavHeader
NavigationViewSeparator = SideNavSeparator

__all__ = [
    'SideNav',
    'SideNavGroup',
    'SideNavItem',
    'SideNavHeader',
    'SideNavSeparator',
    # Backward compatibility
    'NavigationView',
    'NavigationViewItem',
    'NavigationViewGroup',
    'NavigationViewHeader',
    'NavigationViewSeparator',
]
