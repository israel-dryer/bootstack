"""A dependency-free polling file watcher for hot reload.

PROVISIONAL — part of the carved-out ``bootstack.dev`` surface.

Runs on its own thread and ONLY enqueues — it never touches Tcl/Tk (the hard
tkinter rule). It compares ``.py`` modification times under the project root on
a short interval and calls back with the set of changed paths. A poll keeps the
dev tooling free of a hard ``watchdog`` dependency, which matters while #149
freezes the runtime surface.
"""
from __future__ import annotations

import os
import threading
from typing import Callable


class PollWatcher:
    """Watch ``.py`` files under a directory tree and report changes by mtime."""

    def __init__(
        self,
        root: str,
        on_change: Callable[[set[str]], None],
        *,
        interval: float = 0.3,
        suffixes: tuple[str, ...] = (".py",),
    ) -> None:
        self._root = os.path.abspath(root)
        self._on_change = on_change
        self._interval = interval
        self._suffixes = suffixes
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        # Per-file (mtime, size): size catches a same-tick save whose mtime did
        # not advance past the filesystem's coarse resolution.
        self._snapshot: dict[str, tuple[float, int]] = {}

    def start(self) -> None:
        """Take a baseline snapshot and begin watching on a daemon thread."""
        self._snapshot = self._scan()
        self._thread = threading.Thread(
            target=self._loop, name="bootstack-dev-watcher", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the watch thread to exit (does not block)."""
        self._stop.set()

    # --- internals -----------------------------------------------------------

    def _loop(self) -> None:
        while not self._stop.wait(self._interval):
            try:
                current = self._scan()
            except OSError:
                continue
            changed = {
                path
                for path, stamp in current.items()
                if self._snapshot.get(path) != stamp
            }
            # Deletions also count as changes worth a reload attempt.
            changed |= {p for p in self._snapshot if p not in current}
            if changed:
                self._snapshot = current
                try:
                    self._on_change(changed)
                except Exception:
                    # The watcher thread must never die on a callback error.
                    pass

    def _scan(self) -> dict[str, tuple[float, int]]:
        result: dict[str, tuple[float, int]] = {}
        # Symlinked directories are not followed (os.walk default) — avoids cycles.
        for dirpath, dirnames, filenames in os.walk(self._root):
            # Skip the usual noise so a save doesn't churn over caches/venvs.
            dirnames[:] = [
                d for d in dirnames
                if d not in {"__pycache__", ".git", ".venv", "venv", "node_modules", ".mypy_cache"}
            ]
            for name in filenames:
                if name.endswith(self._suffixes):
                    full = os.path.join(dirpath, name)
                    try:
                        st = os.stat(full)
                        result[full] = (st.st_mtime, st.st_size)
                    except OSError:
                        continue
        return result