"""Platform configuration paths for bootstack apps.

A single home for the per-platform config directory convention so window-state
persistence, `Store`, and anything else that writes user state all agree on
where files live.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

__all__ = ["user_config_dir", "app_config_dir", "app_config_file"]


def user_config_dir() -> Path:
    """Return the OS user-configuration base directory.

    `~/Library/Application Support` on macOS, `%APPDATA%` on Windows, and
    `$XDG_CONFIG_HOME` (falling back to `~/.config`) elsewhere.
    """
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))


def app_config_dir(app_name: str | None = None) -> Path:
    """Return the per-app config directory under `user_config_dir()`.

    The leaf is `app_name` (or `'bootstack'` when not given) so multiple
    bootstack apps on one machine do not collide.

    Args:
        app_name: The application name, used as the directory leaf.
    """
    return user_config_dir() / (app_name or "bootstack")


def app_config_file(filename: str, app_name: str | None = None) -> Path:
    """Return the path to a named file inside the per-app config directory.

    Args:
        filename: The leaf file name (for example `'settings.json'`).
        app_name: The application name, used as the directory leaf.
    """
    return app_config_dir(app_name) / filename
