"""Tests for the flat App configuration surface.

Covers the settings-flattening work: configuration as flat constructor kwargs,
symmetric `app.*` properties (read + live write), locale-derived read-only
properties, `App.from_store` version-skew tolerance, and the removal of the
public `AppSettings` / `settings=` surface.
"""
from __future__ import annotations

import pytest

import bootstack as bs

pytestmark = pytest.mark.isolated


@pytest.fixture
def make_app():
    """Factory creating public `App`s, all destroyed on teardown."""
    created = []

    def _make(**kwargs):
        app = bs.App(**kwargs)
        app._tk_root.withdraw()
        created.append(app)
        return app

    try:
        yield _make
    finally:
        for app in created:
            try:
                app._tk_root.destroy()
            except Exception:
                pass


@pytest.mark.gui
def test_flat_kwargs_map_to_properties(make_app):
    app = make_app(
        title="Demo",
        theme="bootstrap-dark",
        locale="de_DE",
        remember_window_state=True,
        window_style=None,
        macos_quit_behavior="classic",
    )
    assert app.title == "Demo"
    assert app.theme == "bootstrap-dark"
    assert app.locale == "de_DE"
    assert app.remember_window_state is True
    assert app.window_style is None


@pytest.mark.gui
def test_theme_setter_is_live(make_app):
    app = make_app(theme="bootstrap-dark")
    assert app.theme == "bootstrap-dark"
    app.theme = "bootstrap-light"
    assert app.theme == "bootstrap-light"
    assert bs.style.get_theme() == "bootstrap-light"


@pytest.mark.gui
def test_locale_derived_properties_are_read_only(make_app):
    app = make_app(locale="de_DE")
    assert app.locale_language == "de"
    assert app.locale_decimal == ","
    assert app.locale_thousands == "."
    assert app.locale_date_format  # non-empty derived pattern
    with pytest.raises(AttributeError):
        app.locale_date_format = "yyyy-MM-dd"


@pytest.mark.gui
def test_locale_setter_updates_derived(make_app):
    app = make_app(locale="en_US")
    assert app.locale_decimal == "."
    app.locale = "de_DE"
    assert app.locale == "de_DE"
    assert app.locale_decimal == ","


@pytest.mark.gui
def test_from_store_ignores_unknown_keys(make_app):
    # Simulate version skew: a stale key that is no longer a valid App kwarg.
    store = {"theme": "bootstrap-dark", "locale": "fr_FR", "bogus_old_key": 123}
    # plain App(**store) would raise TypeError; from_store filters it out.
    app = bs.App.from_store(store)
    app._tk_root.withdraw()
    try:
        assert app.theme == "bootstrap-dark"
        assert app.locale == "fr_FR"
    finally:
        app._tk_root.destroy()


@pytest.mark.gui
def test_from_store_overrides_win(make_app):
    store = {"theme": "bootstrap-dark"}
    app = bs.App.from_store(store, theme="bootstrap-light")
    app._tk_root.withdraw()
    try:
        assert app.theme == "bootstrap-light"
    finally:
        app._tk_root.destroy()


def test_no_public_appsettings_surface():
    # Configuration is flat kwargs + properties; the old object surface is gone.
    assert not hasattr(bs, "AppSettings")
    assert not hasattr(bs, "get_app_settings")


@pytest.mark.gui
def test_settings_kwarg_rejected(make_app):
    # Pre-release clean break: there is no settings= shim.
    with pytest.raises(TypeError):
        make_app(settings={"theme": "bootstrap-dark"})
