"""Grid geometry manager capabilities mixin for bootstack widgets."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from typing_extensions import Self, Unpack


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


class GridMixin:
    """Grid geometry manager helpers (grid).

    Tk's `grid` geometry manager arranges widgets in a table of rows and columns.

    In bootstack v2 you may prefer higher-level layout containers (e.g. `GridFrame`)
    for most UI layout. This mixin documents the underlying Tkinter `grid_*` API
    as an escape hatch and for interoperability with existing Tk code.

    Notes:
        - `grid()` attaches a widget to a parent container that is using grid.
        - `grid_rowconfigure()` / `grid_columnconfigure()` set sizing behavior.
        - `grid_propagate(False)` prevents a container from resizing to fit its children.
        - If the parent has a `_on_child_grid` hook (e.g. GridFrame), layout defaults
          are applied automatically.
    """

    # -------------------------------------------------------------------------
    # Core widget methods
    # -------------------------------------------------------------------------

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
        if hasattr(parent, '_on_child_grid'):
            parent._on_child_grid(self, **options)
        else:
            super().grid(**options)  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def grid_configure(self, cnf: dict[str, Any] | None = None, **kw: Unpack[GridKwargs]) -> Self:
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
        if hasattr(parent, '_on_child_grid_forget'):
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
        if hasattr(parent, '_on_child_grid_remove'):
            parent._on_child_grid_remove(self)
        else:
            super().grid_remove()  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def grid_info(self) -> dict[str, Any]:
        """Return this widget's current grid configuration.

        Returns:
            A dict containing the current grid options for this widget
            (row, column, sticky, padx, pady, etc.).
        """
        return super().grid_info()  # type: ignore[misc]

    # -------------------------------------------------------------------------
    # Container methods (applied to the grid parent container)
    # -------------------------------------------------------------------------

    def grid_propagate(self, flag: bool | None = None) -> bool | None:
        """Get or set grid geometry propagation for this container.

        When propagation is enabled (default), the container may resize itself
        to fit the size requests of its children.

        Args:
            flag: True/False to enable/disable propagation. If None, acts as a getter.

        Returns:
            When queried, returns the current propagation flag. When set, returns None.
        """
        return super().grid_propagate(flag)  # type: ignore[misc]

    def grid_rowconfigure(self, index: int, cnf: dict[str, Any] | None = None, **kw: Unpack[GridRowColumnKwargs]) -> None:
        """Configure sizing behavior for a grid row in this container.

        Args:
            index: Row index (0-based).
            cnf: Optional dict of configuration options (same keys as `GridRowColumnKwargs`).
            **kw: See `GridRowColumnKwargs`.
        """
        if cnf is None:
            return super().grid_rowconfigure(index, **kw)  # type: ignore[misc]
        return super().grid_rowconfigure(index, cnf, **kw)  # type: ignore[misc]

    def grid_columnconfigure(self, index: int, cnf: dict[str, Any] | None = None, **kw: Unpack[GridRowColumnKwargs]) -> None:
        """Configure sizing behavior for a grid column in this container.

        Args:
            index: Column index (0-based).
            cnf: Optional dict of configuration options (same keys as `GridRowColumnKwargs`).
            **kw: See `GridRowColumnKwargs`.
        """
        if cnf is None:
            return super().grid_columnconfigure(index, **kw)  # type: ignore[misc]
        return super().grid_columnconfigure(index, cnf, **kw)  # type: ignore[misc]

    def grid_size(self) -> tuple[int, int]:
        """Return the grid size (columns, rows) used in this container.

        Returns:
            A tuple (num_columns, num_rows).
        """
        return super().grid_size()  # type: ignore[misc]

    def grid_slaves(
            self,
            row: int | None = None,
            column: int | None = None,
    ) -> list[Any]:
        """Return the widgets managed by grid in this container.

        Args:
            row: If provided, return only widgets in the given row.
            column: If provided, return only widgets in the given column.

        Returns:
            A list of child widgets managed by grid.
        """
        if row is None and column is None:
            return super().grid_slaves()  # type: ignore[misc]
        if row is None:
            return super().grid_slaves(column=column)  # type: ignore[misc]
        if column is None:
            return super().grid_slaves(row=row)  # type: ignore[misc]
        return super().grid_slaves(row=row, column=column)  # type: ignore[misc]
