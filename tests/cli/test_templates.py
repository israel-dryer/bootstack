"""Tests for the bootstack CLI templating mechanism.

These tests exercise create_project / create_view / create_page /
create_dialog. Each generated file is parsed (Python via ast, TOML via
tomllib) so that broken format strings or schema drift fail loudly.

Tests do NOT execute the generated apps — that would require Tk and is
covered (manually) by the editable-install workflow in
``analysis/cli-testing.md``.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

from bootstack.cli.config import TtkbConfig
from bootstack.cli.pyinstaller import SPEC_TEMPLATE, generate_spec
from bootstack.cli.templates import (
    create_dialog,
    create_page,
    create_project,
    create_view,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _assert_python_parses(path: Path) -> ast.Module:
    """Parse a .py file with ast and return the module node."""
    src = path.read_text(encoding="utf-8")
    return ast.parse(src, filename=str(path))


def _load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


# ---------------------------------------------------------------------------
# create_project: basic template
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("container", ["grid", "pack"])
@pytest.mark.parametrize("simple", [False, True])
def test_create_basic_project(tmp_path: Path, container: str, simple: bool) -> None:
    target = tmp_path / "myapp"
    create_project(
        name="MyApp",
        target_dir=target,
        container=container,
        theme="cosmo",
        template="basic",
        simple=simple,
    )

    # Required files
    assert (target / "src" / "myapp" / "main.py").is_file()
    assert (target / "src" / "myapp" / "__init__.py").is_file()
    assert (target / "src" / "myapp" / "views" / "main_view.py").is_file()
    assert (target / "src" / "myapp" / "views" / "__init__.py").is_file()
    assert (target / "bootstack.toml").is_file()

    # Simple flag controls README and assets/
    assert (target / "README.md").is_file() != simple
    assert (target / "assets").is_dir() != simple

    # Generated Python parses
    for py in (target / "src" / "myapp").rglob("*.py"):
        _assert_python_parses(py)

    # bootstack.toml round-trips and carries the right fields
    cfg = _load_toml(target / "bootstack.toml")
    assert cfg["app"]["name"] == "MyApp"
    assert cfg["app"]["template"] == "basic"
    assert cfg["app"]["entry"] == "src/myapp/main.py"
    assert "settings" not in cfg  # runtime config is not a toml concern
    assert "build" not in cfg  # promote adds it later

    # main.py bakes the chosen theme as a literal and references the right view
    # subclass for the chosen container.
    main_src = (target / "src" / "myapp" / "main.py").read_text(encoding="utf-8")
    assert 'theme="cosmo"' in main_src
    assert "from myapp.views.main_view import build_main" in main_src

    # The view is a builder function, not a class.
    view_path = target / "src" / "myapp" / "views" / "main_view.py"
    view_src = view_path.read_text(encoding="utf-8")
    funcs = [n.name for n in ast.walk(_assert_python_parses(view_path)) if isinstance(n, ast.FunctionDef)]
    assert "build_main" in funcs
    if container == "grid":
        assert "bs.Grid" in view_src
    else:
        assert "bs.Column" not in view_src  # pack view paints directly, no wrapper


# ---------------------------------------------------------------------------
# create_project: appshell template
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("simple", [False, True])
def test_create_appshell_project(tmp_path: Path, simple: bool) -> None:
    target = tmp_path / "myshell"
    create_project(
        name="MyShell",
        target_dir=target,
        theme="superhero",
        template="appshell",
        simple=simple,
    )

    assert (target / "src" / "myshell" / "main.py").is_file()
    assert (target / "src" / "myshell" / "pages" / "home_page.py").is_file()
    assert (target / "src" / "myshell" / "pages" / "settings_page.py").is_file()
    assert (target / "src" / "myshell" / "pages" / "__init__.py").is_file()

    # Basic-template artifacts must not appear
    assert not (target / "src" / "myshell" / "views").exists()

    for py in (target / "src" / "myshell").rglob("*.py"):
        _assert_python_parses(py)

    cfg = _load_toml(target / "bootstack.toml")
    assert cfg["app"]["template"] == "appshell"
    assert "settings" not in cfg  # runtime config is not a toml concern

    main_src = (target / "src" / "myshell" / "main.py").read_text(encoding="utf-8")
    assert "bs.AppShell" in main_src
    assert 'theme="superhero"' in main_src
    # Pages are wired in as builder functions, called inside add_page() blocks.
    assert "build_home()" in main_src and "build_settings()" in main_src
    home_path = target / "src" / "myshell" / "pages" / "home_page.py"
    home_funcs = [
        n.name for n in ast.walk(_assert_python_parses(home_path))
        if isinstance(n, ast.FunctionDef)
    ]
    assert "build_home" in home_funcs
    # The page builder paints directly into the page region — no inner wrapper.
    assert "bs.Column" not in home_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Name normalization
# ---------------------------------------------------------------------------


def test_create_project_normalizes_hyphenated_name(tmp_path: Path) -> None:
    target = tmp_path / "out"
    create_project(
        name="My-Cool App",
        target_dir=target,
        template="basic",
        simple=True,
    )
    # Module dir uses snake_case derived from the name
    assert (target / "src" / "my_cool_app" / "main.py").is_file()
    cfg = _load_toml(target / "bootstack.toml")
    assert cfg["app"]["entry"] == "src/my_cool_app/main.py"


# ---------------------------------------------------------------------------
# Component scaffolders
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("container", ["grid", "pack"])
def test_create_view(tmp_path: Path, container: str) -> None:
    out = create_view("ProfileView", tmp_path, container=container)
    assert out.name == "profile_view.py"
    mod = _assert_python_parses(out)
    funcs = [n.name for n in ast.walk(mod) if isinstance(n, ast.FunctionDef)]
    assert "build_profile" in funcs
    src = out.read_text(encoding="utf-8")
    if container == "grid":
        assert "bs.Grid" in src
    else:
        assert "bs.Column" not in src  # pack view paints directly


def test_create_dialog(tmp_path: Path) -> None:
    out = create_dialog("ConfirmDialog", tmp_path)
    assert out.name == "confirm_dialog.py"
    mod = _assert_python_parses(out)
    classes = [n.name for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]
    assert "ConfirmDialog" in classes


def test_create_page_camel_to_snake(tmp_path: Path) -> None:
    out = create_page("DashboardPage", tmp_path)
    assert out.name == "dashboard_page.py"
    mod = _assert_python_parses(out)
    funcs = [n.name for n in ast.walk(mod) if isinstance(n, ast.FunctionDef)]
    # Builder function strips the trailing 'Page' suffix
    assert "build_dashboard" in funcs
    # Page title strips trailing 'Page' for the heading
    src = out.read_text(encoding="utf-8")
    assert '"Dashboard"' in src


# ---------------------------------------------------------------------------
# PyInstaller spec template
# ---------------------------------------------------------------------------


def test_spec_template_format_is_safe() -> None:
    """SPEC_TEMPLATE.format(...) must render without KeyError on stray
    f-string braces (regression: {CONFIG_PATH} was once unescaped)."""
    rendered = SPEC_TEMPLATE.format(app_name="Demo")
    # Generated spec is parseable Python
    ast.parse(rendered)
    # Spot-check that the literal Python f-string survived as f-string
    assert "f\"bootstack.toml not found at {CONFIG_PATH}\"" in rendered


def test_default_launch_icon_is_packaged() -> None:
    """The spec template falls back to bootstack/assets/bootstack.ico
    when no [build.icon] is set; the file must ship with the package."""
    import bootstack
    icon = Path(bootstack.__file__).parent / "assets" / "bootstack.ico"
    assert icon.is_file(), f"missing default launch icon: {icon}"
    rendered = SPEC_TEMPLATE.format(app_name="Demo")
    assert "bootstack.ico" in rendered, (
        "spec template no longer references the bundled default icon — "
        "the previous path 'assets/icons/app.ico' silently failed because "
        "that file never existed in the package"
    )



def test_spec_template_uses_specpath_not_dunder_file() -> None:
    """Spec files are exec'd by PyInstaller without ``__file__`` in the
    namespace; ``SPECPATH`` is the supported way to locate the spec dir.

    ``module.__file__`` references (e.g. ``bootstack.__file__``) are
    fine — only a bare ``__file__`` lookup is broken.
    """
    rendered = SPEC_TEMPLATE.format(app_name="Demo")
    # Bare __file__ references look like Path(__file__), not foo.__file__
    assert "Path(__file__)" not in rendered, (
        "spec template references bare __file__ which is undefined when "
        "PyInstaller exec's the spec — use SPECPATH instead"
    )
    assert "SPECPATH" in rendered


def test_generate_spec_writes_parseable_file(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    create_project(name="SpecApp", target_dir=target, template="basic", simple=True)
    cfg = TtkbConfig.load(target / "bootstack.toml")
    spec_path = target / "build" / "pyinstaller" / "app.spec"
    generate_spec(cfg, target, spec_path)
    assert spec_path.is_file()
    ast.parse(spec_path.read_text(encoding="utf-8"))


def test_spec_template_includes_copy_metadata() -> None:
    """The spec must call copy_metadata('bootstack') so that
    importlib.metadata.version() resolves inside the frozen bundle.
    Without it, bootstack/__init__.py raises PackageNotFoundError on launch."""
    rendered = SPEC_TEMPLATE.format(app_name="Demo")
    assert "copy_metadata" in rendered, (
        "spec template no longer calls copy_metadata — the dist-info directory "
        "won't be bundled and importlib.metadata.version('bootstack') will raise "
        "PackageNotFoundError in the frozen app"
    )
