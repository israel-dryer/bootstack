from __future__ import annotations

from typing import Mapping, Any, Callable, TypedDict, Unpack, Self


class ClipboardKwargs(TypedDict, total=False):
    """Keyword options accepted by clipboard operations."""

    displayof: Any
    """Widget or window whose display to target. Omit for the main application display."""
    type: str
    """Clipboard type name (e.g., `'STRING'`, `'UTF8_STRING'`). Platform-dependent."""
    format: str
    """Data format for representing selection data to the X server (e.g., `'STRING'`). Platform-dependent."""


class GridKwargs(TypedDict, total=False):
    """Keyword options for `grid()` and `grid_configure()`."""

    row: int
    """Row index (0-based). Defaults to the next available row."""
    column: int
    """Column index (0-based). Defaults to 0."""
    rowspan: int
    """Number of rows to span. Defaults to 1."""
    columnspan: int
    """Number of columns to span. Defaults to 1."""
    sticky: str
    """How the widget expands within its cell (e.g., `'nsew'`, `'ew'`, `'n'`). Defaults to `''`."""
    padx: int | tuple[int, int]
    """Horizontal external padding in pixels. A tuple sets (left, right) independently."""
    pady: int | tuple[int, int]
    """Vertical external padding in pixels. A tuple sets (top, bottom) independently."""
    ipadx: int
    """Horizontal internal padding in pixels."""
    ipady: int
    """Vertical internal padding in pixels."""
    in_: Any
    """Parent widget to grid into (rarely needed — defaults to the widget's own master)."""


class GridRowColumnKwargs(TypedDict, total=False):
    """Keyword options for `grid_rowconfigure()` and `grid_columnconfigure()`."""

    weight: int
    """How extra space is distributed among rows/columns. 0 means no expansion. Defaults to 0."""
    minsize: int
    """Minimum row/column size in pixels. Defaults to 0."""
    pad: int
    """Extra padding added to the row/column in pixels. Defaults to 0."""
    uniform: str
    """Group name — rows/columns sharing a group are given equal size."""


class PackKwargs(TypedDict, total=False):
    """Keyword options for `pack()` and `pack_configure()`."""

    side: str
    """Side to pack against — `'top'`, `'bottom'`, `'left'`, or `'right'`. Defaults to `'top'`."""
    fill: str
    """How to fill extra space — `'x'`, `'y'`, `'both'`, or `'none'`. Defaults to `'none'`."""
    expand: bool | int
    """If True/1, the widget expands to fill extra space in the packing direction. Defaults to False."""
    anchor: str
    """Where to place the widget when it does not fill available space (e.g., `'center'`, `'nw'`). Defaults to `'center'`."""
    padx: int | tuple[int, int]
    """Horizontal external padding in pixels. A tuple sets (left, right) independently."""
    pady: int | tuple[int, int]
    """Vertical external padding in pixels. A tuple sets (top, bottom) independently."""
    ipadx: int
    """Horizontal internal padding in pixels."""
    ipady: int
    """Vertical internal padding in pixels."""
    before: Any
    """Pack this widget immediately before the given widget."""
    after: Any
    """Pack this widget immediately after the given widget."""
    in_: Any
    """Parent widget to pack into (rarely needed — defaults to the widget's own master)."""


class WidgetCapabilitiesMixin:
    """Common widget API surface (tk + ttk).

    This mixin aggregates documented capability mixins into a single interface
    suitable for both Tk and ttk widgets, plus a small set of commonly used
    widget operations (configure/cget/destroy, stacking order, etc.).
    """

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def destroy(self) -> None:
        """Destroy this widget and release its Tk resources."""
        return super().destroy()  # type: ignore[misc]

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    def configure(self, cnf: Mapping[str, Any] | None = None, **kw: Any) -> Any:
        """Configure widget options.

        Args:
            cnf: Optional mapping of option values.
            **kw: Option values as keyword arguments.

        Returns:
            Tk returns configuration details when called with no args; otherwise
            the return value is implementation-dependent.
        """
        if cnf is None:
            return super().configure(**kw)  # type: ignore[misc]
        return super().configure(cnf, **kw)  # type: ignore[misc]

    config = configure

    def cget(self, key: str) -> Any:
        """Return the current value for an option.

        Args:
            key: Option name (with or without a leading dash).

        Returns:
            The option value.
        """
        return super().cget(key)  # type: ignore[misc]

    # -------------------------------------------------------------------------
    # Stacking order
    # -------------------------------------------------------------------------

    def lift(self, aboveThis: Any | None = None) -> None:
        """Raise this widget above its siblings.

        Args:
            aboveThis: Optional sibling widget to raise above.
        """
        return super().lift(aboveThis)  # type: ignore[misc]

    tkraise = lift

    def lower(self, belowThis: Any | None = None) -> None:
        """Lower this widget below its siblings.

        Args:
            belowThis: Optional sibling widget to lower below.
        """
        return super().lower(belowThis)  # type: ignore[misc]

    def after_repeat(
        self, ms: int, func: Callable[..., Any], *args: Any
    ) -> Callable[[], None]:
        """Call `func` repeatedly every `ms` milliseconds.

        This helper schedules `func` and then automatically reschedules it after
        each run. It returns a `cancel()` function you can call to stop repetition.

        Args:
            ms: Interval in milliseconds.
            func: Callback to run each interval.
            *args: Arguments to pass to `func`.

        Returns:
            A `cancel()` callable. Call it to stop the repeating schedule.

        Examples:
            >>> cancel = widget.after_repeat(250, tick)
            >>> cancel()
        """
        cancelled = False
        token: str | None = None

        def _run():
            nonlocal token
            if cancelled:
                return
            func(*args)
            token = self.after(ms, _run)

        token = self.after(ms, _run)

        def cancel() -> None:
            nonlocal cancelled, token
            cancelled = True
            if token is not None:
                try:
                    self.after_cancel(token)
                except Exception:
                    pass
                token = None

        return cancel

    def bindtags_prepend(self, tag: str) -> tuple[str, ...]:
        """Prepend a tag to the bindtags list.

        This increases the tag's priority (it will be processed earlier).

        Args:
            tag: Tag name to prepend.

        Returns:
            The updated bindtags tuple.
        """
        current = list(self.bindtags())
        if tag not in current:
            current.insert(0, tag)
            self.bindtags(current)
        return tuple(current)

    def bindtags_append(self, tag: str) -> tuple[str, ...]:
        """Append a tag to the bindtags list.

        This decreases the tag's priority (it will be processed later).

        Args:
            tag: Tag name to append.

        Returns:
            The updated bindtags tuple.
        """
        current = list(self.bindtags())
        if tag not in current:
            current.append(tag)
            self.bindtags(current)
        return tuple(current)

    def bindtags_remove(self, tag: str) -> tuple[str, ...]:
        """Remove a tag from the bindtags list.

        Args:
            tag: Tag name to remove.

        Returns:
            The updated bindtags tuple.
        """
        current = [t for t in self.bindtags() if t != tag]
        self.bindtags(current)
        return tuple(current)

    def bindtags_replace(self, old: str, new: str) -> tuple[str, ...]:
        """Replace a bindtag with another tag.

        Args:
            old: Existing tag name.
            new: Replacement tag name.

        Returns:
            The updated bindtags tuple.
        """
        current = list(self.bindtags())
        try:
            idx = current.index(old)
        except ValueError:
            return tuple(current)
        current[idx] = new
        self.bindtags(current)
        return tuple(current)

    def clipboard_set(self, text: str, **kw: Unpack[ClipboardKwargs]) -> None:
        """Replace clipboard contents with *text*.

        Convenience wrapper for `clipboard_clear()` + `clipboard_append()`.

        Args:
            text: Text to set on the clipboard.
            **kw: See `ClipboardKwargs`. Forwarded to both clear and append.
        """
        self.clipboard_clear(**kw)
        self.clipboard_append(text, **kw)

    def grid(self, cnf: dict[str, Any] | None = None, **kw: Unpack[GridKwargs]) -> Self:
        """Position this widget using the grid geometry manager.

        Args:
            cnf: Optional dict of grid options (same keys as `GridKwargs`).
            **kw: See `GridKwargs`.

        Returns:
            Self for method chaining.
        """
        options = cnf or {}
        options.update(kw)

        parent = self.master  # type: ignore[attr-defined]
        if hasattr(parent, "_on_child_grid"):
            parent._on_child_grid(self, **options)
        else:
            super().grid(**options)  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def grid_configure(
        self, cnf: dict[str, Any] | None = None, **kw: Unpack[GridKwargs]
    ) -> Self:
        """Alias for `grid()`.

        Args:
            cnf: Optional dict of grid options.
            **kw: See `GridKwargs`.

        Returns:
            Self for method chaining.
        """
        return self.grid(cnf, **kw)

    def grid_forget(self) -> Self:
        """Unmap this widget and forget its grid configuration.

        The widget is removed from the layout, and its previous grid options
        are discarded.

        Returns:
            Self for method chaining.
        """
        parent = self.master  # type: ignore[attr-defined]
        if hasattr(parent, "_on_child_grid_forget"):
            parent._on_child_grid_forget(self)
        else:
            super().grid_forget()  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def grid_remove(self) -> Self:
        """Unmap this widget but remember its grid configuration.

        Use `grid()` with no args to restore it to its previous grid location.

        Returns:
            Self for method chaining.
        """
        parent = self.master  # type: ignore[attr-defined]
        if hasattr(parent, "_on_child_grid_remove"):
            parent._on_child_grid_remove(self)
        else:
            super().grid_remove()  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def pack(self, cnf: dict[str, Any] | None = None, **kw: Unpack[PackKwargs]) -> Self:
        """Position this widget using the pack geometry manager.

        Args:
            cnf: Optional dict of pack options (same keys as `PackKwargs`).
            **kw: See `PackKwargs`.

        Returns:
            Self for method chaining.
        """
        options = cnf or {}
        options.update(kw)

        parent = self.master  # type: ignore[attr-defined]
        if hasattr(parent, "_on_child_pack"):
            parent._on_child_pack(self, **options)
        else:
            super().pack(**options)  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def pack_configure(
        self, cnf: dict[str, Any] | None = None, **kw: Unpack[PackKwargs]
    ) -> Self:
        """Alias for `pack()`.

        Args:
            cnf: Optional dict of pack options.
            **kw: See `PackKwargs`.

        Returns:
            Self for method chaining.
        """
        return self.pack(cnf, **kw)

    def pack_forget(self) -> Self:
        """Unmap this widget and forget its pack configuration.

        The widget is removed from the layout, and its previous pack options
        are discarded.

        Returns:
            Self for method chaining.
        """
        parent = self.master  # type: ignore[attr-defined]
        if hasattr(parent, "_on_child_pack_forget"):
            parent._on_child_pack_forget(self)
        else:
            super().pack_forget()  # type: ignore[misc]
        return self  # type: ignore[return-value]
