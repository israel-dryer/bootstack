"""Tk command interception for the edit filter chain.

Port of IDLE's `idlelib/redirector.py`. The rest of this package already ports
that design rather than importing it — `filter.py` adapts Delegator and
Percolator, `undo.py` adapts UndoDelegator, `sidebar.py` and
`extensions/line_numbers.py` port the sidebar — and this was the one piece left
as a live import. `idlelib` is standard library, but not every Python build
ships it, so that import made the whole framework unimportable on those builds
rather than degrading the code editor.

A Tk widget is backed by a Tcl command named after the widget's path, and every
operation on the widget goes through it — including the ones Tk's own key
bindings perform, which never reach Python at all. Renaming that command and
putting a dispatcher in its place is what lets the filter chain see an insert
that came from a keystroke, which is the whole reason this exists.
"""
from __future__ import annotations

import tkinter as tk
from typing import Any, Callable


class WidgetRedirector:
    """Intercepts operations on a Tk widget, including the toolkit's own.

    Renames the widget's Tcl command out of the way and installs a dispatcher
    under the original name. Registered operations are routed to a Python
    callable; everything else passes straight through to the renamed command.

    Only one redirector can exist for a given widget — the rename fails once
    the name it renames to is taken.

    Args:
        widget: The widget whose operations are to be intercepted.
    """

    def __init__(self, widget: tk.Misc) -> None:
        self._operations: dict[str, Callable[..., Any]] = {}
        self.widget = widget
        self.tk = widget.tk
        path = widget._w
        self.orig = path + "_orig"
        self.tk.call("rename", path, self.orig)
        self.tk.createcommand(path, self.dispatch)

    def register(
        self, operation: str, function: Callable[..., Any]
    ) -> OriginalCommand:
        """Route `operation` to `function`, returning a way to call the original.

        The function is also set on the widget, so a call written in Python —
        `text.insert(...)` — is intercepted the same way a keystroke is.
        Registering a second function for the same operation replaces the first
        in both places.

        Args:
            operation: Name of the widget operation, such as `insert`.
            function: What to call in its place. It receives the operation's
                arguments, and is handed the returned callable to pass the call
                on with.
        """
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return OriginalCommand(self, operation)

    def unregister(self, operation: str) -> Callable[..., Any] | None:
        """Stop routing `operation`, returning whatever was handling it.

        Returns None if the operation was not registered. Dropping the widget
        attribute that `register` set unmasks the widget's own method again.

        Args:
            operation: Name of the widget operation to stop intercepting.
        """
        function = self._operations.pop(operation, None)
        if function is None:
            return None
        try:
            delattr(self.widget, operation)
        except AttributeError:
            pass
        return function

    def dispatch(self, operation, *args):
        """Handle one call to the widget, invoked from Tcl.

        A registered operation goes to its function and does not continue on to
        the widget — the function decides whether to pass the call along, using
        the callable it was given at registration. Everything else goes
        straight through.

        Args:
            operation: The operation being performed. Tcl may hand this over as
                its own object type rather than a string.
            args: The operation's arguments, exactly as Tcl passed them.
        """
        operation = str(operation)
        function = self._operations.get(operation)
        try:
            if function is not None:
                return function(*args)
            return self.tk.call((self.orig, operation) + args)
        except tk.TclError:
            # What the toolkit itself does with a failed widget command. The
            # caller here is Tcl, which has nowhere useful to put an exception.
            return ""

    def close(self) -> None:
        """Undo the interception and restore the widget's own Tcl command."""
        for operation in list(self._operations):
            self.unregister(operation)
        path = self.widget._w
        self.tk.deletecommand(path)
        self.tk.call("rename", self.orig, path)


class OriginalCommand:
    """The widget operation a redirector displaced, as a plain callable.

    Returned by `WidgetRedirector.register` so a registered function can pass
    the call on to the widget after inspecting or changing it. Calling this
    reaches the widget directly and does not re-enter the chain.

    Args:
        redirector: The redirector that displaced the operation.
        operation: Name of the displaced operation.
    """

    def __init__(self, redirector: WidgetRedirector, operation: str) -> None:
        self._operation = operation
        self._call = redirector.tk.call
        self._target = (redirector.orig, operation)

    def __call__(self, *args):
        return self._call(self._target + args)

    def __repr__(self) -> str:
        return f"OriginalCommand({self._operation!r})"
