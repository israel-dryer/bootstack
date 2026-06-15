"""Configuration loader and writer for bootstack.toml."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Python 3.11+ has tomllib built-in, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

# Default bootstack.toml template
DEFAULT_CONFIG_TEMPLATE = """\
[app]
name = "{name}"
id = "{app_id}"
entry = "{entry}"
template = "{template}"

[layout]
default_container = "grid"
"""

BUILD_CONFIG_TEMPLATE = """\

[build]
backend = "pyinstaller"
windowed = true      # GUI app with no console window (false to keep a console)
onefile = true       # one executable (false for a folder, which starts faster)

# Modules PyInstaller misses (add the ones your app fails to import at runtime),
# and modules to leave out of the build:
# hidden_imports = ["some_package"]
# excludes = ["tkinter.test"]

# This file is a starting point. For any PyInstaller option not covered here,
# edit the generated spec at build/pyinstaller/app.spec directly — it is a
# standard PyInstaller spec and is only regenerated with
# `bootstack promote --pyinstaller --force`.

[build.icon]
# Point at an existing icon file (a single file, or per-platform art):
# path = "assets/icon.ico"
# windows = "assets/icon.ico"
# macos = "assets/icon.icns"
# ...or generate one from a Bootstrap icon glyph — rendered in the host
# platform's format at build time. Colors must be hex values (theme tokens
# cannot be resolved at build time, when no app is running):
# glyph = "rocket"
# shape = "auto"          # auto | tile | glyph (auto: glyph-only small, tile large)
# background = "#0d6efd"
# foreground = "#ffffff"
# radius = 0.22

[build.datas]
include = [
    "assets/**",
    "locales/**",
    "themes/**",
    "bootstack.toml",
]
"""


@dataclass
class AppConfig:
    """The [app] section of bootstack.toml."""

    name: str = "MyApp"
    id: str = "com.example.myapp"
    entry: str = "src/myapp/main.py"
    template: str = "basic"


@dataclass
class LayoutConfig:
    """The [layout] section of bootstack.toml."""

    default_container: str = "grid"  # grid | pack


@dataclass
class BuildIconConfig:
    """The [build.icon] section of bootstack.toml.

    Either point `path` at an existing icon file, or set `glyph` to generate an
    icon from a Bootstrap icon at build time. Generated-icon colors must be hex
    values — theme tokens cannot be resolved during a build, when no application
    is running.
    """

    path: Optional[str] = None
    windows: Optional[str] = None
    macos: Optional[str] = None
    linux: Optional[str] = None
    glyph: Optional[str] = None
    shape: str = "auto"
    background: str = "#0d6efd"
    foreground: str = "#ffffff"
    radius: float = 0.22


@dataclass
class BuildDatasConfig:
    """The [build.datas] section of bootstack.toml."""

    include: list[str] = field(default_factory=list)


@dataclass
class BuildConfig:
    """The [build] section of bootstack.toml."""

    backend: str = "pyinstaller"
    windowed: bool = True
    onefile: bool = True
    hidden_imports: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    icon: BuildIconConfig = field(default_factory=BuildIconConfig)
    datas: BuildDatasConfig = field(default_factory=BuildDatasConfig)


@dataclass
class TtkbConfig:
    """Complete bootstack.toml configuration."""

    app: AppConfig = field(default_factory=AppConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    build: Optional[BuildConfig] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TtkbConfig:
        """Create TtkbConfig from a dictionary (parsed TOML)."""
        app_data = data.get("app", {})
        layout_data = data.get("layout", {})
        build_data = data.get("build")

        app = AppConfig(
            name=app_data.get("name", "MyApp"),
            id=app_data.get("id", "com.example.myapp"),
            entry=app_data.get("entry", "src/myapp/main.py"),
            template=app_data.get("template", "basic"),
        )

        layout = LayoutConfig(
            default_container=layout_data.get("default_container", "grid"),
        )

        build = None
        if build_data is not None:
            icon_data = build_data.get("icon", {})
            datas_data = build_data.get("datas", {})

            build = BuildConfig(
                backend=build_data.get("backend", "pyinstaller"),
                windowed=build_data.get("windowed", True),
                onefile=build_data.get("onefile", True),
                hidden_imports=build_data.get("hidden_imports", []),
                excludes=build_data.get("excludes", []),
                icon=BuildIconConfig(
                    path=icon_data.get("path"),
                    windows=icon_data.get("windows"),
                    macos=icon_data.get("macos"),
                    linux=icon_data.get("linux"),
                    glyph=icon_data.get("glyph"),
                    shape=icon_data.get("shape", "auto"),
                    background=icon_data.get("background", "#0d6efd"),
                    foreground=icon_data.get("foreground", "#ffffff"),
                    radius=float(icon_data.get("radius", 0.22)),
                ),
                datas=BuildDatasConfig(include=datas_data.get("include", [])),
            )

        return cls(app=app, layout=layout, build=build)

    @classmethod
    def load(cls, path: Path | str = "bootstack.toml") -> TtkbConfig:
        """Load configuration from a bootstack.toml file.

        Args:
            path: Path to the configuration file.

        Returns:
            TtkbConfig instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            RuntimeError: If TOML parsing is not available.
        """
        if tomllib is None:
            raise RuntimeError(
                "TOML parsing not available. Install 'tomli' package: pip install tomli"
            )
        path = Path(path)
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls.from_dict(data)

    @classmethod
    def load_or_default(cls, path: Path | str = "bootstack.toml") -> TtkbConfig:
        """Load configuration from file, or return defaults if not found.

        Args:
            path: Path to the configuration file.

        Returns:
            TtkbConfig instance (loaded or default).
        """
        path = Path(path)
        if path.exists():
            return cls.load(path)
        return cls()


def find_config(start_dir: Path | str | None = None) -> Path | None:
    """Find bootstack.toml by walking up from start_dir.

    Args:
        start_dir: Starting directory (defaults to current working directory).

    Returns:
        Path to bootstack.toml if found, None otherwise.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    else:
        start_dir = Path(start_dir)

    current = start_dir.resolve()
    while current != current.parent:
        config_path = current / "bootstack.toml"
        if config_path.exists():
            return config_path
        current = current.parent

    # Check root
    config_path = current / "bootstack.toml"
    if config_path.exists():
        return config_path

    return None


def generate_config(
    name: str,
    app_id: Optional[str] = None,
    entry: Optional[str] = None,
    theme: str = "bootstrap-light",
    template: str = "basic",
    include_build: bool = False,
) -> str:
    """Generate bootstack.toml content.

    Args:
        name: Application name.
        app_id: Application identifier (defaults to com.example.<name>).
        entry: Entry point path (defaults to src/<name>/main.py).
        theme: Theme name (default: cosmo).
        template: Project template type (default: basic).
        include_build: Whether to include [build] section.

    Returns:
        TOML configuration string.
    """
    name_lower = name.lower().replace(" ", "_").replace("-", "_")
    if app_id is None:
        app_id = f"com.example.{name_lower}"
    if entry is None:
        entry = f"src/{name_lower}/main.py"

    content = DEFAULT_CONFIG_TEMPLATE.format(
        name=name,
        app_id=app_id,
        entry=entry,
        template=template,
    )

    if include_build:
        content += BUILD_CONFIG_TEMPLATE

    return content


def write_config(
    path: Path | str,
    name: str,
    app_id: Optional[str] = None,
    entry: Optional[str] = None,
    theme: str = "bootstrap-light",
    template: str = "basic",
    include_build: bool = False,
) -> None:
    """Write bootstack.toml to disk.

    Args:
        path: Path to write the configuration file.
        name: Application name.
        app_id: Application identifier.
        entry: Entry point path.
        theme: Theme name (default: cosmo).
        template: Project template type (default: basic).
        include_build: Whether to include [build] section.
    """
    path = Path(path)
    content = generate_config(name, app_id, entry, theme, template, include_build)
    path.write_text(content, encoding="utf-8")
