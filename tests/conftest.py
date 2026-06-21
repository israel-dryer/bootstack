"""Shared pytest fixtures for the bootstack test suite.

GUI tests run against a SINGLE Tk root for the whole session. Destroying a Tk
root and creating a new one in the same process crashes natively (ttk
``element_create`` access violation as image-element registrations accumulate
across interpreters), so per-module ``bs.App()`` create/destroy is not viable.
Instead one root is created once (`_session_app`) and each test gets it via the
`app` fixture, which resets the *scene* (destroys the test's widgets, restores
the theme) on teardown — the root, styles, fonts, and images persist.
"""
from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def _session_app():
    """The one Tk root for the entire test session.

    Created once and reused by every GUI test. Never create a second
    ``bs.App()`` in-process — sequential roots crash natively. Created withdrawn
    and NOT entered: the `app`/`shown_app` fixtures push it onto the container
    stack per-test (and pop it after), so the stack is clean between tests.
    """
    import bootstack as bs

    app = bs.App()
    app._tk_root.withdraw()
    app._tk_root.update_idletasks()
    try:
        yield app
    finally:
        try:
            app._tk_root.destroy()
        except Exception:
            pass


def _region(app):
    """The container widgets parent into (the app's content region)."""
    return getattr(app, "_region_root", app._tk_root)


def _snapshot(app) -> set[str]:
    """Paths of all widgets present now — both the app's permanent scaffolding
    (root-level chrome like the toolbar packframe) and content-region children.
    """
    root = app._tk_root
    region = _region(app)
    paths = {str(w) for w in root.winfo_children()}
    paths |= {str(w) for w in region.winfo_children()}
    return paths


def _reset_scene(app, keep: set[str]) -> None:
    """Destroy every widget created since `keep` was snapshotted, keeping root.

    `keep` holds the app's permanent scaffolding (toolbar packframe, content
    region) so only test-created widgets — content, stray toplevels, dialogs,
    chrome toolbars — are torn down.
    """
    root = app._tk_root
    region = _region(app)
    region_path = str(region)
    for w in list(region.winfo_children()):
        if str(w) not in keep:
            try:
                w.destroy()
            except Exception:
                pass
    for w in list(root.winfo_children()):
        path = str(w)
        if path != region_path and path not in keep:
            try:
                w.destroy()
            except Exception:
                pass
    # Reset chrome bookkeeping for anything we just tore down so a later
    # add_toolbar() rebuilds cleanly instead of reusing a destroyed widget.
    ct = getattr(app, "_chrome_toolbars", None)
    if ct is not None:
        kept = []
        for entry in ct:
            tb = entry[0] if isinstance(entry, (tuple, list)) else entry
            try:
                if tb._internal.winfo_exists():
                    kept.append(entry)
            except Exception:
                pass
        app._chrome_toolbars = kept
    # The cached toolbar stack (packframe) is recreated lazily; drop the
    # reference if its widget was destroyed by the scene reset.
    ts = getattr(app, "_toolbar_stack", None)
    if ts is not None:
        try:
            alive = bool(ts.winfo_exists())
        except Exception:
            alive = False
        if not alive:
            app._toolbar_stack = None


@pytest.fixture
def app(_session_app):
    """The shared App for a test, scene-reset afterward for isolation.

    Yields the process-wide :class:`bootstack.App`. Widgets created during the
    test are destroyed on teardown and the theme is restored, so each test
    starts from a clean root without paying for a new interpreter.
    """
    from bootstack.widgets._core.context import push_container, pop_container

    a = _session_app
    keep = _snapshot(a)
    theme_before = locale_before = None
    try:
        theme_before = a.theme
    except Exception:
        pass
    try:
        locale_before = a.locale
    except Exception:
        pass
    push_container(a)  # active parent for this test; popped on teardown
    try:
        yield a
    finally:
        pop_container(a)
        _reset_scene(a, keep)
        # Restore theme/locale so a test that changes them does not bleed into
        # the next test sharing this root.
        if theme_before is not None:
            try:
                if a.theme != theme_before:
                    a.theme = theme_before
            except Exception:
                pass
        if locale_before is not None:
            try:
                if a.locale != locale_before:
                    a.locale = locale_before
            except Exception:
                pass


@pytest.fixture
def shown_app(_session_app):
    """The shared App, mapped on-screen for geometry-dependent tests.

    Some tests need the root realized (deiconified) so widget geometry and
    layout pumps behave. Deiconifies the shared root for the test, then
    withdraws and scene-resets it afterward.
    """
    from bootstack.widgets._core.context import push_container, pop_container

    a = _session_app
    keep = _snapshot(a)
    a._tk_root.deiconify()
    a._tk_root.update_idletasks()
    push_container(a)
    try:
        yield a
    finally:
        pop_container(a)
        _reset_scene(a, keep)
        try:
            a._tk_root.withdraw()
        except Exception:
            pass


@pytest.fixture
def tmp_tk_root(app):
    """The shared root for tests that exercise raw event binding.

    Backed by the session-wide :func:`app` (a bare ``tkinter.Tk()`` can't be
    created once bootstack's autostyle patch is installed). Scene-reset via the
    `app` fixture. Requires a display, so consumers should be marked
    ``@pytest.mark.gui``.
    """
    return app._tk_root
