"""Cross-platform keyboard shortcuts — the public home for the shortcut service.

Register named shortcuts with platform-agnostic patterns (``Mod+S`` becomes
``Ctrl+S`` on Windows/Linux and ``⌘S`` on macOS), bind them to an app, and let
menus display the resolved shortcut text automatically.

Usage::

    import bootstack as bs

    shortcuts = bs.get_shortcuts()
    shortcuts.register("save", "Mod+S", save_file)
    shortcuts.bind_to(app)
"""
from bootstack._runtime.shortcuts import Shortcut, Shortcuts, get_shortcuts

__all__ = [
    "Shortcuts",
    "Shortcut",
    "get_shortcuts",
]
