"""Registry behind ``@reloadable`` for deterministic multi-file hot reload.

PROVISIONAL — part of the carved-out ``bootstack.dev`` surface.

A page builder in another file calls bootstack widgets into whatever container
is active when it runs (the thread-local container stack). ``@reloadable`` marks
such a builder so the reloader can, when only that file changes, re-invoke the
*current* version of the builder into the exact region it last painted —
bypassing the entry module's possibly-stale ``from x import f`` binding and
giving per-page reload granularity.

In production (no dev mode) the decorator is a transparent no-op.
"""
from __future__ import annotations

from typing import Any, Callable

from bootstack.dev._env import is_dev_mode

# qualified-name -> the most recently defined builder function. Reloading a page
# module re-runs its top level, which re-registers the builder under the same
# qualname, so this always points at the live version.
_builders: dict[str, Callable] = {}

# qualified-name -> list of mount records describing where the builder painted,
# so a per-page reload can clear and rebuild just those regions.
_mounts: dict[str, list["MountRecord"]] = {}


class MountRecord:
    """Where a ``@reloadable`` builder painted, for targeted re-invocation."""

    __slots__ = ("container", "args", "kwargs")

    def __init__(self, container: Any, args: tuple, kwargs: dict) -> None:
        self.container = container
        self.args = args
        self.kwargs = kwargs


def reloadable(func: Callable) -> Callable:
    """Mark a builder function as a hot-reload unit (no-op in production).

    Apply to a function that *builds* part of the UI by calling widgets into the
    active container::

        @reloadable
        def build_dashboard(db):
            bs.Label("Dashboard", font="heading-lg")
            bs.DataTable(data_source=db)

    In dev mode the framework records where the builder mounted; when its file is
    saved, only that region is torn down and rebuilt with the new code. Outside
    dev mode the function is returned unchanged.
    """
    if not is_dev_mode():
        return func

    qualname = f"{func.__module__}.{func.__qualname__}"
    # Register at DECORATION time so importlib.reload (which re-runs the module
    # top level, re-decorating) refreshes the builder to the new version. The
    # wrapper then always invokes the current registration.
    _builders[qualname] = func

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from bootstack.widgets._core.context import current_container

        container = current_container()
        if container is not None:
            _mounts.setdefault(qualname, []).append(
                MountRecord(container, args, kwargs)
            )
        return _builders.get(qualname, func)(*args, **kwargs)

    wrapper.__wrapped__ = func  # type: ignore[attr-defined]
    wrapper.__name__ = getattr(func, "__name__", "reloadable")
    wrapper.__qualname__ = getattr(func, "__qualname__", "reloadable")
    wrapper.__doc__ = func.__doc__
    wrapper._bs_reloadable_qualname = qualname  # type: ignore[attr-defined]
    return wrapper


def builders_in_module(module_name: str) -> list[str]:
    """Return the qualnames of registered builders defined in a module."""
    prefix = module_name + "."
    return [q for q in _builders if q.startswith(prefix)]


def reinvoke(qualname: str) -> bool:
    """Clear and rebuild every region a builder painted. Returns True if any ran.

    Used for per-page reload: when only a page file changed, its builder(s) are
    re-invoked into their recorded regions instead of re-running the entry body.
    """
    from bootstack.dev._reset import clear_container
    from bootstack.widgets._core.context import push_container, pop_container

    func = _builders.get(qualname)
    records = _mounts.get(qualname)
    if func is None or not records:
        return False

    ran = False
    for record in list(records):
        container = record.container
        if not _container_alive(container):
            records.remove(record)
            continue
        clear_container(container)
        push_container(container)
        try:
            func(*record.args, **record.kwargs)
            ran = True
        finally:
            pop_container(container)
    return ran


def reset_mounts() -> None:
    """Forget mount records (used before a full rebuild re-records them).

    Builders are kept — they are keyed by qualname and overwritten when their
    module reloads, so there is nothing stale to clear, and dropping them would
    discard registrations from modules that did not reload this pass.
    """
    _mounts.clear()


def reset() -> None:
    """Forget all registered builders and mount records (used on teardown)."""
    _builders.clear()
    _mounts.clear()


def _container_alive(container: Any) -> bool:
    internal = getattr(container, "_internal", container)
    try:
        return bool(internal.winfo_exists())
    except Exception:
        return False