"""EditFilter base class and FilterChain.

Adaptation of IDLE's Delegator/Percolator pattern
(idlelib/delegator.py + idlelib/percolator.py).

WidgetRedirector intercepts every insert/delete at the Tk command level —
including keyboard input from Tk's default text bindings — and routes them
through the Python filter chain. The bottom of the chain calls the original
Tk command via OriginalCommand objects returned by redirector.register(),
which are clean Python callables, not raw Tcl strings.
"""
from __future__ import annotations

import tkinter as tk
from idlelib.redirector import WidgetRedirector
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


# NOTE(editfilter-public-api): EditFilter was demoted from the top-level public
# namespace during the API Reference restructure (Stage 4). It is a Tk-coupled
# extension hook — subclasses work in raw Tk text indices, tags, and the Tk Text
# API — which contradicts the framework's "Tkinter is invisible" premise, and it
# ships no narrative docs. CodeEditor still accepts user filters via
# `extensions=`/`install()`, so it stays importable for power users, but it is no
# longer presented as compose surface. TODO: decide whether CodeEditor should have
# a real, documented, de-Tkinter-ed extension/plugin API (one that hides Tk text
# indices behind framework-level edit events) and, if so, design that as the public
# face — re-promoting only once it no longer leaks Tk. See memory
# project_editfilter_public_api.
class EditFilter:
    """Sits in the mutation chain between user code and the Tk Text widget.

    Subclass and override `insert` and/or `delete` to intercept edits.
    Always forward to `self.delegate.insert` / `self.delegate.delete`
    unless you intend to suppress the edit.

    Attribute reads (`self.get(...)`, `self.tag_add(...)`, etc.) forward
    automatically to the next delegate via `__getattr__`, so a filter
    behaves like the Text widget itself when reading state.
    """

    def __init__(self) -> None:
        self.delegate: EditFilter | _BottomFilter | None = None
        self._cache: set[str] = set()

    def __getattr__(self, name: str):
        if name.startswith('_') or self.delegate is None:
            raise AttributeError(name)
        attr = getattr(self.delegate, name)
        setattr(self, name, attr)
        self._cache.add(name)
        return attr

    def _reset_cache(self) -> None:
        for k in self._cache:
            try:
                delattr(self, k)
            except AttributeError:
                pass
        self._cache.clear()

    def _set_delegate(self, d: EditFilter | _BottomFilter | None) -> None:
        self._reset_cache()
        self.delegate = d

    def insert(self, index: str, chars: str, tags=None) -> None:
        """Forward an insert to the next delegate."""
        self.delegate.insert(index, chars, tags)

    def delete(self, index1: str, index2: str | None = None) -> None:
        """Forward a delete to the next delegate."""
        self.delegate.delete(index1, index2)

    def attach(self, core: _MultilineCore) -> None:
        """Called when this filter is added to a core's chain."""

    def detach(self, core: _MultilineCore) -> None:
        """Called when this filter is removed from a core's chain."""


class _BottomFilter:
    """Terminal filter — calls the original Tk Text command via OriginalCommand.

    WidgetRedirector.register() returns an OriginalCommand callable for each
    intercepted operation. Calling it routes directly to the renamed Tcl proc
    (e.g. `.!text_orig insert ...`) without going back through the chain.
    """

    def __init__(self, orig_insert, orig_delete, text: tk.Text) -> None:
        self._orig_insert = orig_insert   # OriginalCommand returned by register()
        self._orig_delete = orig_delete   # OriginalCommand returned by register()
        self._text = text

    def __getattr__(self, name: str):
        return getattr(self._text, name)

    def insert(self, index: str, chars: str, tags=None) -> None:
        if tags:
            self._orig_insert(index, chars, tags)
        else:
            self._orig_insert(index, chars)

    def delete(self, index1: str, index2: str | None = None) -> None:
        if index2 is not None:
            self._orig_delete(index1, index2)
        else:
            self._orig_delete(index1)

    def _set_delegate(self, d) -> None:
        pass


class FilterChain:
    """Owns the ordered chain of EditFilters.

    Uses WidgetRedirector so that every insert/delete on the Text widget —
    including those triggered by Tk's default key bindings — flows through
    the chain before reaching the underlying Tk Text widget.
    """

    def __init__(self, text: tk.Text) -> None:
        self._text = text
        self._redirector = WidgetRedirector(text)
        self._filters: list[EditFilter] = []

        # Register our handlers; register() returns OriginalCommand callables
        orig_insert = self._redirector.register('insert', self._chain_insert)
        orig_delete = self._redirector.register('delete', self._chain_delete)

        self._bottom = _BottomFilter(orig_insert, orig_delete, text)
        self._top: EditFilter | _BottomFilter = self._bottom

    def _chain_insert(self, index: str, chars: str, tags=None) -> None:
        self._top.insert(index, chars, tags)

    def _chain_delete(self, index1: str, index2: str | None = None) -> None:
        self._top.delete(index1, index2)

    def add(self, f: EditFilter) -> None:
        """Prepend a filter to the top of the chain."""
        f._set_delegate(self._top)
        self._top = f
        self._filters.insert(0, f)

    def remove(self, f: EditFilter) -> None:
        """Remove a filter from the chain."""
        if f not in self._filters:
            return
        idx = self._filters.index(f)
        above = self._filters[idx - 1] if idx > 0 else None
        below = self._filters[idx + 1] if idx < len(self._filters) - 1 else self._bottom

        if above is None:
            self._top = below
        else:
            above._set_delegate(below)

        f._set_delegate(None)
        self._filters.pop(idx)

    def destroy(self) -> None:
        """Uninstall the redirector."""
        try:
            self._redirector.unregister('insert')
            self._redirector.unregister('delete')
            self._redirector.close()
        except Exception:
            pass
