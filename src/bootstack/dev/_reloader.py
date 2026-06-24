"""The hot-reload engine: watch, re-exec, recover.

PROVISIONAL — part of the carved-out ``bootstack.dev`` surface.

Two strategies, chosen in :func:`install_reloader`:

* **in-process** (default) — on save, re-read the entry file, reset the region
  the ``with`` body built, and re-exec the body in place. Module-level state
  (signals, datasources, stores) lives outside the body and survives. Multi-file
  edits reload the changed page modules first; ``@reloadable`` builders rebuild
  just their own region.
* **restart** — on save, exit with a sentinel code so the ``bootstack dev``
  supervisor relaunches the process. The floor for apps that aren't a
  module-level ``with bs.App()``; window geometry is persisted so it re-opens
  where it was. (We avoid ``os.execv``: on Windows it does not replace the
  process in place.)

The watcher only enqueues; all Tk work happens on a main-thread ``after`` pump,
so the one tkinter threading rule is never broken.
"""
from __future__ import annotations

import os
import queue
import sys
import traceback
from typing import Any

from bootstack.dev._capture import BodyCapture, compile_body, find_current_body
from bootstack.dev._env import dev_mode, is_dev_mode
from bootstack.dev._watcher import PollWatcher

_PREFIX = "[bootstack dev]"


def _project_watch_root(start: str) -> str:
    """Widen the watch root from a starting file to the project tree.

    Walks up from `start` looking for a `bootstack.toml`; when found, watches its
    `src/` subtree if present (the conventional layout) else the project dir — so
    edits to any module in the project, not just the entry file's directory, are
    picked up. Falls back to the starting file's directory when no project marker
    is found.
    """
    start = os.path.abspath(start)
    cur = start if os.path.isdir(start) else os.path.dirname(start)
    base = cur
    for _ in range(40):  # bounded walk-up
        if os.path.isfile(os.path.join(cur, "bootstack.toml")):
            src = os.path.join(cur, "src")
            return src if os.path.isdir(src) else cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return base


def install_reloader(app: Any) -> None:
    """Install the appropriate reloader for the running app, if in dev mode."""
    if not is_dev_mode():
        return
    mode = dev_mode()
    supports = getattr(app, "_dev_supports_inprocess", False)
    capture: BodyCapture | None = getattr(app, "_dev_body", None)
    in_process_ok = supports and capture is not None and capture.is_capturable

    if mode == "restart" or not in_process_ok:
        if mode != "restart":
            if not supports:
                _log(
                    "in-process reload isn't supported for this app type yet - "
                    "using process restart on save"
                )
            elif capture is None or not capture.is_capturable:
                _log(
                    "in-process reload needs a module-level `with bs.App()` - "
                    "using process restart on save"
                )
        _RestartReloader(app).install()
        return

    _InProcessReloader(app, capture).install()


def _log(message: str) -> None:
    print(f"{_PREFIX} {message}", flush=True)


class _BaseReloader:
    """Shared watcher + main-thread pump plumbing."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.root = app._internal
        self._queue: "queue.Queue[set[str]]" = queue.Queue()
        self._watcher: PollWatcher | None = None
        self._pump_id: Any = None

    def _watch_root(self) -> str:
        raise NotImplementedError

    def install(self) -> None:
        self._watcher = PollWatcher(self._watch_root(), self._queue.put)
        self._watcher.start()
        self._schedule_pump()

    def _schedule_pump(self) -> None:
        try:
            self._pump_id = self.root.after(120, self._pump)
        except Exception:
            self._pump_id = None

    def _pump(self) -> None:
        changed: set[str] = set()
        try:
            while True:
                changed |= self._queue.get_nowait()
        except queue.Empty:
            pass
        if changed:
            try:
                self._handle(changed)
            except Exception:
                traceback.print_exc()
        try:
            if self.root.winfo_exists():
                self._schedule_pump()
        except Exception:
            pass

    def _handle(self, changed: set[str]) -> None:
        raise NotImplementedError


class _RestartReloader(_BaseReloader):
    """Re-exec the whole process on save (the robust floor)."""

    def install(self) -> None:
        super().install()
        _log(f"watching for changes - process restart on save (mode={dev_mode()})")

    def _watch_root(self) -> str:
        entry = sys.argv[0] if sys.argv and sys.argv[0] else os.getcwd()
        return _project_watch_root(entry) or os.getcwd()

    def _handle(self, changed: set[str]) -> None:
        _log("change detected - restarting")
        if self._watcher is not None:
            self._watcher.stop()
        # Persist geometry (and, for a shell, the selected page) so the
        # relaunched process re-opens in place. We exit immediately, skipping
        # destroy, so save now.
        for attr in ("_save_window_state", "_save_nav_state"):
            save = getattr(self.app._internal, attr, None)
            if callable(save):
                try:
                    save()
                except Exception:
                    pass
        sys.stdout.flush()
        sys.stderr.flush()
        # Ask the `bootstack dev` supervisor to relaunch us by exiting with the
        # sentinel code. We do NOT os.execv: on Windows it spawns a new process
        # and terminates this one, orphaning the app and dropping the supervisor
        # after the first reload. os._exit skips interpreter cleanup/atexit — the
        # supervisor owns the new process's lifecycle.
        from bootstack.dev._env import DEV_RESTART_EXIT_CODE

        os._exit(DEV_RESTART_EXIT_CODE)


class _InProcessReloader(_BaseReloader):
    """Reset and re-exec the ``with`` body in place, preserving module state."""

    def __init__(self, app: Any, capture: BodyCapture) -> None:
        super().__init__(app)
        self.capture = capture
        self._error_banner: Any = None

    def install(self) -> None:
        super().install()
        rel = os.path.relpath(self.capture.filename)
        _log(f"hot reload active - editing {rel} updates the running app on save")

    def _watch_root(self) -> str:
        return _project_watch_root(self.capture.filename)

    def _handle(self, changed: set[str]) -> None:
        entry = os.path.abspath(self.capture.filename)
        changed_abs = {os.path.abspath(p) for p in changed}
        entry_changed = entry in changed_abs
        page_files = changed_abs - {entry}

        try:
            # Per-page fast path: the entry is unchanged AND every changed file is a
            # module that holds registered @reloadable builders — rebuild just those
            # regions, skip the entry body. A changed module WITHOUT a builder
            # (constants/models with module-level state) must take the full path:
            # importlib.reload would otherwise split object identity (fresh objects
            # while live widgets still hold the old ones) without rebinding. (#326)
            builder_files = set(self._builder_module_files())
            if not entry_changed and page_files and page_files <= builder_files:
                reloaded = self._reload_modules(page_files)
                if reloaded and self._reinvoke_pages(reloaded):
                    self._clear_error()
                    self.app._dev_after_rebuild()
                    _log("reloaded " + ", ".join(sorted(reloaded)))
                    return

            # Full reload: reload any changed project modules first (so the re-exec'd
            # entry body rebinds to the fresh objects), then re-run the body.
            self._reload_modules(page_files)
            self._full_reload()
            self._clear_error()
            _log("reloaded")
        except SyntaxError as exc:
            self._show_error(_format_syntax_error(exc))
            _log("syntax error - fix and save again")
        except Exception:
            self._show_error(traceback.format_exc())
            _log("reload failed - see the banner; fix and save again")

    def _full_reload(self) -> None:
        # Compile BEFORE tearing down, so a syntax error never blanks the UI.
        body = find_current_body(self.capture)
        code = compile_body(self.capture.filename, body)

        route = _safe(self.app._dev_capture_route)
        self.app._dev_reset_region()

        from bootstack.widgets._core.context import push_container, pop_container

        push_container(self.app)
        try:
            exec(code, self.capture.module_globals)
        finally:
            pop_container(self.app)

        self.app._dev_after_rebuild()
        if route is not None:
            try:
                self.app._dev_restore_route(route)
            except Exception:
                pass

    def _reinvoke_pages(self, modules: set[str]) -> bool:
        from bootstack.dev import _registry

        ran = False
        for module in modules:
            for qualname in _registry.builders_in_module(module):
                if _registry.reinvoke(qualname):
                    ran = True
        return ran

    def _builder_module_files(self) -> dict[str, str]:
        """Map abspath -> module name for loaded modules holding registered builders."""
        from bootstack.dev import _registry

        out: dict[str, str] = {}
        for name, module in list(sys.modules.items()):
            path = getattr(module, "__file__", None)
            if path and _registry.builders_in_module(name):
                out[os.path.abspath(path)] = name
        return out

    def _reload_modules(self, files: set[str]) -> set[str]:
        """importlib.reload any loaded project module whose file changed."""
        if not files:
            return set()
        import importlib

        reloaded: set[str] = set()
        for name, module in list(sys.modules.items()):
            path = getattr(module, "__file__", None)
            if not path:
                continue
            if os.path.abspath(path) in files:
                importlib.reload(module)  # exceptions surface as a banner
                reloaded.add(name)
        return reloaded

    # --- error banner --------------------------------------------------------

    def _show_error(self, text: str) -> None:
        import tkinter as tk

        self._clear_error()
        # `_content_frame` is an attribute on App but a method on AppShell/
        # Workbench — resolve both to the content widget that hosts the banner.
        frame = getattr(self.app, "_content_frame", None)
        if callable(frame):
            frame = frame()
        if frame is None:
            sys.stderr.write(text + "\n")
            return
        try:
            banner = tk.Frame(frame, background="#2b0f10")
            banner.place(relx=0, rely=0, relwidth=1, relheight=1)
            tk.Label(
                banner,
                text="Hot reload failed - fix the error and save again",
                background="#2b0f10",
                foreground="#ff7b72",
                font=("TkDefaultFont", 11, "bold"),
                anchor="w",
            ).pack(fill="x", padx=14, pady=(12, 4))
            body = tk.Text(
                banner,
                background="#2b0f10",
                foreground="#ffd7d5",
                relief="flat",
                borderwidth=0,
                wrap="word",
                padx=14,
                pady=4,
                highlightthickness=0,
            )
            body.insert("1.0", text)
            body.configure(state="disabled")
            body.pack(fill="both", expand=True)
            self._error_banner = banner
        except Exception:
            sys.stderr.write(text + "\n")

    def _clear_error(self) -> None:
        banner = self._error_banner
        self._error_banner = None
        if banner is not None:
            try:
                banner.destroy()
            except Exception:
                pass


def _safe(fn: Any) -> Any:
    try:
        return fn()
    except Exception:
        return None


def _format_syntax_error(exc: SyntaxError) -> str:
    where = f"{exc.filename}:{exc.lineno}"
    parts = [f"SyntaxError: {exc.msg}", f"  at {where}"]
    if exc.text:
        parts.append("  " + exc.text.rstrip())
        if exc.offset:
            parts.append("  " + " " * (exc.offset - 1) + "^")
    return "\n".join(parts)