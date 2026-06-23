"""Unit tests for the dev hot-reload machinery (bootstack.dev).

These are root-free: they exercise the capture/registry/env/watcher logic and
the install-strategy decision without constructing a Tk root, so they run in the
ordinary (non-GUI) test process. GUI integration of an actual reload lives in
tests/widgets/public/test_hot_reload_*.py (isolated).
"""
from __future__ import annotations

import os
import textwrap

import pytest


# --- environment detection ---------------------------------------------------


def test_is_dev_mode_reads_env(monkeypatch):
    from bootstack.dev._env import is_dev_mode, dev_mode

    monkeypatch.delenv("BOOTSTACK_DEV", raising=False)
    assert is_dev_mode() is False

    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    assert is_dev_mode() is True

    monkeypatch.setenv("BOOTSTACK_DEV", "0")
    assert is_dev_mode() is False


def test_dev_mode_default_and_values(monkeypatch):
    from bootstack.dev._env import dev_mode

    monkeypatch.delenv("BOOTSTACK_DEV_MODE", raising=False)
    assert dev_mode() == "inprocess"
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "restart")
    assert dev_mode() == "restart"
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "garbage")
    assert dev_mode() == "inprocess"


def test_dev_min_size_is_reasonable():
    from bootstack.dev._env import DEV_MIN_SIZE

    w, h = DEV_MIN_SIZE
    assert w >= 320 and h >= 240


# --- body capture ------------------------------------------------------------


def _write(tmp_path, name, src):
    path = tmp_path / name
    path.write_text(textwrap.dedent(src), encoding="utf-8")
    return str(path)


def test_capture_requires_module_level(monkeypatch):
    from bootstack.dev._capture import capture_from_frame
    import sys

    # A frame whose locals IS globals (module level) is capturable; a function
    # frame (locals != globals) is not.
    def inside_function():
        return capture_from_frame(sys._getframe(0))

    assert inside_function() is None


def test_capture_and_find_body_by_target_name(tmp_path, monkeypatch):
    from bootstack.dev import _capture

    path = _write(tmp_path, "app.py", """
        x = 1
        with open(__file__) as f:   # a stand-in `with ... as <name>` block
            a = 1
            b = 2
    """)
    # Build a capture by hand pointing at the file's with-block target `f`.
    cap = _capture.BodyCapture(
        filename=path, target_names=("f",), module_globals={}, with_lineno=2
    )
    body = _capture.find_current_body(cap)
    # The block body is the two assignments.
    assert len(body) == 2

    code = _capture.compile_body(path, body)
    ns: dict = {}
    exec(code, ns)
    assert ns["a"] == 1 and ns["b"] == 2


def test_find_body_survives_line_shift(tmp_path):
    from bootstack.dev import _capture

    path = _write(tmp_path, "app.py", """
        with open(__file__) as handle:
            value = 99
    """)
    cap = _capture.BodyCapture(
        filename=path, target_names=("handle",), module_globals={}, with_lineno=2
    )
    # Insert lines above the with-block; matching is by target name, not line.
    new = "import os\nimport sys\n\n" + (tmp_path / "app.py").read_text()
    (tmp_path / "app.py").write_text(new, encoding="utf-8")
    body = _capture.find_current_body(cap)
    code = _capture.compile_body(path, body)
    ns: dict = {}
    exec(code, ns)
    assert ns["value"] == 99


def test_find_body_syntax_error_propagates(tmp_path):
    from bootstack.dev import _capture

    path = _write(tmp_path, "app.py", """
        with open(__file__) as f:
            ok = 1
    """)
    cap = _capture.BodyCapture(
        filename=path, target_names=("f",), module_globals={}, with_lineno=2
    )
    (tmp_path / "app.py").write_text("with open(x) as f:\n    ok = (\n", encoding="utf-8")
    with pytest.raises(SyntaxError):
        _capture.find_current_body(cap)


# --- @reloadable registry ----------------------------------------------------


def test_reloadable_is_noop_outside_dev(monkeypatch):
    monkeypatch.delenv("BOOTSTACK_DEV", raising=False)
    import importlib
    from bootstack.dev import _registry

    importlib.reload(_registry)

    def builder():
        return "built"

    wrapped = _registry.reloadable(builder)
    assert wrapped is builder  # returned unchanged, zero overhead


def test_reloadable_registers_and_reinvokes(monkeypatch):
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    import importlib
    from bootstack.dev import _registry

    importlib.reload(_registry)

    calls = []

    @_registry.reloadable
    def build(tag):
        calls.append(tag)

    qualname = build._bs_reloadable_qualname
    assert qualname in _registry.builders_in_module(__name__) or \
        qualname.startswith(__name__)

    # A fake container the registry can clear + re-invoke into.
    class _Frame:
        def winfo_children(self):
            return []

    class _Container:
        _flex_frame = _Frame()
        _internal = type("I", (), {"winfo_exists": lambda self: True})()

    from bootstack.widgets._core.context import push_container, pop_container

    container = _Container()
    push_container(container)
    try:
        build("first")
    finally:
        pop_container(container)
    assert calls == ["first"]

    # Reinvoking rebuilds into the recorded region with the current builder.
    assert _registry.reinvoke(qualname) is True
    assert calls == ["first", "first"]

    _registry.reset()
    assert _registry.reinvoke(qualname) is False


# --- watcher -----------------------------------------------------------------


def test_pollwatcher_scan_detects_change(tmp_path):
    from bootstack.dev._watcher import PollWatcher

    (tmp_path / "a.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "note.txt").write_text("ignored", encoding="utf-8")

    captured = []
    watcher = PollWatcher(str(tmp_path), captured.append)
    snap = watcher._scan()
    # Only .py files are tracked.
    assert any(p.endswith("a.py") for p in snap)
    assert not any(p.endswith("note.txt") for p in snap)

    # A changed mtime shows up against the snapshot.
    import os, time
    target = str(tmp_path / "a.py")
    os.utime(target, (snap[target] + 5, snap[target] + 5))
    snap2 = watcher._scan()
    changed = {p for p, m in snap2.items() if snap.get(p) != m}
    assert target in changed


def test_pollwatcher_skips_pycache(tmp_path):
    from bootstack.dev._watcher import PollWatcher

    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "x.py").write_text("# cached", encoding="utf-8")
    (tmp_path / "real.py").write_text("x = 1", encoding="utf-8")

    watcher = PollWatcher(str(tmp_path), lambda c: None)
    snap = watcher._scan()
    assert any(p.endswith("real.py") for p in snap)
    assert not any("__pycache__" in p for p in snap)


# --- install-strategy decision (the regression guard) ------------------------


class _StubApp:
    """A minimal app stand-in for the install decision (no Tk)."""

    def __init__(self, *, supports, capturable):
        if supports:
            self._dev_supports_inprocess = True
        self._internal = object()
        if capturable:
            from bootstack.dev._capture import BodyCapture

            self._dev_body = BodyCapture(
                filename="x.py", target_names=("app",), module_globals={}, with_lineno=1
            )
        else:
            self._dev_body = None


@pytest.fixture
def _record_install(monkeypatch):
    chosen = {}
    import bootstack.dev._reloader as rl

    def make(name):
        class _Rec:
            def __init__(self, app, *a, **k):
                chosen["which"] = name

            def install(self):
                chosen["installed"] = True

        return _Rec

    monkeypatch.setattr(rl, "_InProcessReloader", make("inprocess"))
    monkeypatch.setattr(rl, "_RestartReloader", make("restart"))
    return chosen


def test_install_picks_inprocess_when_supported(monkeypatch, _record_install):
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "inprocess")
    from bootstack.dev._reloader import install_reloader

    install_reloader(_StubApp(supports=True, capturable=True))
    assert _record_install["which"] == "inprocess"


def test_install_falls_back_without_support_flag(monkeypatch, _record_install):
    # This is exactly the bug that shipped: a capturable body but the app type
    # lacks _dev_supports_inprocess -> must fall back to restart, not silently
    # pick in-process (and never claim in-process when it can't do it).
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "inprocess")
    from bootstack.dev._reloader import install_reloader

    install_reloader(_StubApp(supports=False, capturable=True))
    assert _record_install["which"] == "restart"


def test_install_restart_mode_forces_restart(monkeypatch, _record_install):
    monkeypatch.setenv("BOOTSTACK_DEV", "1")
    monkeypatch.setenv("BOOTSTACK_DEV_MODE", "restart")
    from bootstack.dev._reloader import install_reloader

    install_reloader(_StubApp(supports=True, capturable=True))
    assert _record_install["which"] == "restart"


def test_install_noop_outside_dev(monkeypatch, _record_install):
    monkeypatch.delenv("BOOTSTACK_DEV", raising=False)
    from bootstack.dev._reloader import install_reloader

    install_reloader(_StubApp(supports=True, capturable=True))
    assert "which" not in _record_install
