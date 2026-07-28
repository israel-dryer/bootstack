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

    The root is genuinely mapped before the test runs, not merely asked to be.
    `deiconify()` is a request the window server services on its own schedule,
    and `update_idletasks()` does not process the resulting map event at all --
    it only runs idle callbacks. A test asserting `winfo_ismapped()` on a child
    therefore depended on how much work happened to be queued ahead of it, which
    is why the macOS `PageStack` keep-mapped tests passed alone and failed in a
    full run (#379).
    """
    from bootstack.widgets._core.context import push_container, pop_container

    a = _session_app
    keep = _snapshot(a)
    a._tk_root.deiconify()
    for _ in range(100):
        a._tk_root.update()
        if a._tk_root.winfo_ismapped():
            break
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


# ---------------------------------------------------------------------------
# Menu backend
# ---------------------------------------------------------------------------
#
# `ContextMenu` picks its implementation from the windowing system: an
# overrideredirect Toplevel of themed widgets everywhere, a real `tk.Menu`
# (NSMenu) on macOS. The two expose entirely different internals -- `_items`
# and `_toplevel` versus `_menu` -- so a test that reaches for one of them
# passes on Windows and Linux and errors out on macOS.
#
# `menu_probe` reads whichever backend is in play, so a test can assert the
# same fact on every platform instead of asserting the Windows shape and
# skipping elsewhere (a skip would leave the macOS path untested while looking
# covered).


class MenuBackendProbe:
    """Backend-agnostic introspection of a `ContextMenu` implementation.

    Each method takes the backend object -- `menu._internal._impl`, or the
    `_context_menu` a widget such as `SelectButton` builds.
    """

    @staticmethod
    def is_native(impl) -> bool:
        """Whether `impl` is the native `tk.Menu` backend (macOS)."""
        from bootstack.widgets._impl.composites.contextmenu import _NativeContextMenu

        return isinstance(impl, _NativeContextMenu)

    def item_count(self, impl) -> int:
        """Number of entries in the menu, separators included.

        Both backends count separators, so the two agree on the same menu.
        """
        if self.is_native(impl):
            # `tk.Menu.index('end')` is None for an empty menu, not -1.
            end = impl._menu.index("end")
            return 0 if end is None else end + 1
        return len(impl._items)

    def item_disabled(self, impl, index: int) -> bool:
        """Whether the entry at `index` is disabled. A separator never is.

        Asked for a separator's state the native backend raises `TclError`
        rather than reporting one, while the themed backend answers `False`.
        Normalized here — otherwise this helper would answer on Windows and
        Linux and blow up on macOS, the very split it exists to remove.
        """
        if self.is_native(impl):
            try:
                return str(impl._menu.entrycget(index, "state")) == "disabled"
            except Exception:
                return False
        return "disabled" in list(impl._items.values())[index].state()

    def popup_toplevel(self, impl):
        """The popup's own Toplevel, or `None` on the native backend.

        The native menu is drawn by the window server and owns no widget tree,
        so there is nothing for a bindtag walk to reach.
        """
        return getattr(impl, "_toplevel", None)


@pytest.fixture(scope="session")
def menu_probe() -> MenuBackendProbe:
    """Backend-agnostic reader for whichever `ContextMenu` backend is active."""
    return MenuBackendProbe()


@pytest.fixture(scope="session")
def menus_are_native(_session_app) -> bool:
    """Whether this platform renders menus natively (macOS/aqua).

    The same check `ChromeHostMixin._menus_are_native` makes, so a test asserts
    against the platform's real behavior rather than a hardcoded expectation.
    """
    try:
        return _session_app._tk_root.tk.call("tk", "windowingsystem") == "aqua"
    except Exception:
        return False
