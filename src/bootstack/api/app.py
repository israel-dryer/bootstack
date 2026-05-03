"""Public application and window API surface.

Application, window management, menu, and shortcuts functionality.
"""

from __future__ import annotations

from bootstack.runtime.app import App, AppSettings, Window, get_app_settings, get_current_app
from bootstack.runtime.toplevel import Toplevel
from bootstack.runtime.menu import MenuManager, create_menu
from bootstack.runtime.shortcuts import Shortcuts, Shortcut, get_shortcuts
from bootstack.widgets.composites.appshell import AppShell

__all__ = [
    # Application
    "App",
    "AppShell",
    "Window",
    "Toplevel",
    "AppSettings",
    "get_current_app",
    "get_app_settings",
    # Menu
    "MenuManager",
    "create_menu",
    # Shortcuts
    "Shortcuts",
    "Shortcut",
    "get_shortcuts",
]
