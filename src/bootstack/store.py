"""`Store` — a small, file-backed key-value store for application preferences.

`Store` is the place to keep the little pieces of state an app wants to remember
between runs: the chosen theme, a "show tips on startup" flag, recent files, the
last-opened tab. It behaves like a dict, persists to a JSON file under the OS
config directory, and writes through on every change by default.

It is deliberately *not* a data source — there are no rows, ids, pagination, or
queries. Reach for `MemoryDataSource` / `SqliteDataSource` for record-oriented
data, and `Store` for "remember this setting".
"""

from __future__ import annotations

import copy
import json
import os
import threading
from pathlib import Path
from typing import Any, Iterator

from bootstack._core.paths import app_config_file
from bootstack.errors import SerializationError

__all__ = ["Store"]

_MISSING = object()


def _active_app_name() -> str | None:
    """Return the current App's name, or None when there is no active App."""
    try:
        from bootstack._runtime.app import get_app_settings

        return get_app_settings().app_name
    except Exception:
        return None


class Store:
    """A persistent, dict-like key-value store for app preferences.

    Construct one with a logical name and it lives at `<config>/<app>/<name>.json`
    (the per-platform config directory — `Library/Application Support` on macOS,
    `%APPDATA%` on Windows, `$XDG_CONFIG_HOME` on Linux), or pass an explicit
    `path`. Read with `get()` or `store[key]`, write with `set()` or
    `store[key] = value`; by default every change is saved immediately with an
    atomic write, so a crash cannot corrupt the file.

    Values must be JSON-serializable (scalars, lists, dicts); anything else
    raises `SerializationError`. Keys must be strings. A missing or unreadable
    file simply starts the store empty rather than raising.

    `Store` does not require a running `App` — it is plain file I/O. When no
    `app_name` is given it uses the active App's name if there is one, otherwise
    `'bootstack'`.

    Args:
        name: Logical store name; the file is `<name>.json` under the per-app
            config directory. Ignored when `path` is given.
        path: An explicit file path, overriding `name`/`app_name`.
        app_name: Override the per-app config sub-directory. Defaults to the
            active App's name, or `'bootstack'`.
        autosave: When True (default), persist on every change. When False,
            changes stay in memory until `save()` is called.

    Example:
        ```python
        store = bs.Store("settings")
        app = bs.App(theme=store.get("theme", "light"))
        # later, when the user switches theme:
        store.set("theme", "bootstrap-dark")
        ```
    """

    def __init__(
        self,
        name: str = "settings",
        *,
        path: str | os.PathLike[str] | None = None,
        app_name: str | None = None,
        autosave: bool = True,
    ) -> None:
        if path is not None:
            self._path = Path(path)
        else:
            if not name:
                raise ValueError("Store: provide a name or an explicit path=.")
            leaf = str(name)
            if not leaf.endswith(".json"):
                leaf = f"{leaf}.json"
            self._path = app_config_file(leaf, app_name or _active_app_name())
        self._autosave = autosave
        self._lock = threading.RLock()
        self._data: dict[str, Any] = {}
        self._load()

    # ----- persistence -----

    def _load(self) -> None:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            self._data = {}
            return
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            # A corrupt file starts the store empty — prefs are not worth
            # crashing an app over.
            self._data = {}
            return
        self._data = data if isinstance(data, dict) else {}

    def save(self) -> None:
        """Write the store to disk now, atomically.

        Useful when `autosave=False`, or to force a flush. Writes to a temporary
        file and renames it over the target so a partial write never replaces
        good data.

        Raises:
            OSError: If the directory cannot be created or the file written.
        """
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_name(f"{self._path.name}.tmp")
            try:
                tmp.write_text(
                    json.dumps(self._data, indent=2, sort_keys=True),
                    encoding="utf-8",
                )
                os.replace(tmp, self._path)
            except BaseException:
                try:
                    tmp.unlink()
                except OSError:
                    pass
                raise

    def reload(self) -> None:
        """Discard in-memory state and re-read the store from disk."""
        with self._lock:
            self._load()

    def _autosaved(self) -> None:
        if self._autosave:
            self.save()

    @staticmethod
    def _check_key(key: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(
                f"Store keys must be strings, got {type(key).__name__}."
            )

    @staticmethod
    def _check_value(key: str, value: Any) -> None:
        try:
            json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise SerializationError(
                f"Store value for key {key!r} is not JSON-serializable: {exc}. "
                f"A Store holds JSON values only (scalars, lists, dicts)."
            ) from exc

    @property
    def path(self) -> Path:
        """The file this store reads from and writes to."""
        return self._path

    # ----- core access -----

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for `key`, or `default` if it is not present."""
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set `key` to `value` and (by default) persist immediately.

        Args:
            key: A string key.
            value: A JSON-serializable value.

        Raises:
            TypeError: If `key` is not a string.
            SerializationError: If `value` is not JSON-serializable.
        """
        self._check_key(key)
        self._check_value(key, value)
        with self._lock:
            self._data[key] = value
            self._autosaved()

    def delete(self, key: str) -> None:
        """Remove `key` if present; a no-op when it is missing."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                self._autosaved()

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Return `key`'s value, inserting `default` first if it is missing."""
        self._check_key(key)
        with self._lock:
            if key not in self._data:
                self._check_value(key, default)
                self._data[key] = default
                self._autosaved()
            return self._data[key]

    def update(self, values: "dict[str, Any]") -> None:
        """Merge a mapping of values in, persisting once at the end."""
        for key, value in values.items():
            self._check_key(key)
            self._check_value(key, value)
        with self._lock:
            if values:
                self._data.update(values)
                self._autosaved()

    def clear(self) -> None:
        """Remove every key, persisting the now-empty store."""
        with self._lock:
            if self._data:
                self._data.clear()
                self._autosaved()

    def keys(self) -> list[str]:
        """Return the keys, as a list snapshot."""
        with self._lock:
            return list(self._data.keys())

    def values(self) -> list[Any]:
        """Return the values, as a list snapshot."""
        with self._lock:
            return list(self._data.values())

    def items(self) -> list[tuple[str, Any]]:
        """Return the `(key, value)` pairs, as a list snapshot."""
        with self._lock:
            return list(self._data.items())

    def as_dict(self) -> dict[str, Any]:
        """Return a deep copy of the store's contents as a plain dict."""
        with self._lock:
            return copy.deepcopy(self._data)

    # ----- mapping protocol -----

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        with self._lock:
            del self._data[key]
            self._autosaved()

    def __contains__(self, key: object) -> bool:
        with self._lock:
            return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def __repr__(self) -> str:
        return f"Store(path={str(self._path)!r}, keys={len(self)})"
