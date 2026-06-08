from __future__ import annotations

from typing import Any, TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from typing_extensions import Self, Unpack


class PlaceKwargs(TypedDict, total=False):
    """Keyword options for `place()` and `place_configure()`."""
    x: int
    """Absolute x-coordinate in pixels, relative to the container's top-left corner."""
    y: int
    """Absolute y-coordinate in pixels, relative to the container's top-left corner."""
    relx: float
    """Relative x-coordinate as a fraction (0.0–1.0) of the container's width."""
    rely: float
    """Relative y-coordinate as a fraction (0.0–1.0) of the container's height."""
    width: int
    """Absolute width of the widget in pixels."""
    height: int
    """Absolute height of the widget in pixels."""
    relwidth: float
    """Width as a fraction (0.0–1.0) of the container's width."""
    relheight: float
    """Height as a fraction (0.0–1.0) of the container's height."""
    anchor: str
    """Which point of the widget is placed at (x, y)/(relx, rely) (e.g., `'nw'`, `'center'`, `'se'`). Defaults to `'nw'`."""
    bordermode: str
    """How x/y are interpreted relative to container borders — `'inside'`, `'outside'`, or `'ignore'`."""
    in_: Any
    """Parent widget to place into (rarely needed — defaults to the widget's own master)."""


class PlaceMixin:
    """Place geometry manager helpers (place).

    Tk's `place` geometry manager positions widgets using absolute coordinates
    and/or relative fractions of the container size.

    `place` is useful for:
        - overlays (badges, floating buttons, popovers)
        - precise positioning inside a fixed-size container
        - small "anchor" adjustments that don't fit grid/pack well

    Notes:
        - `place` is generally less adaptive than `grid` or `pack` for resizable UIs.
        - Relative coordinates (`relx`, `rely`, `relwidth`, `relheight`) are fractions
          of the container size (0.0–1.0).
    """

    # -------------------------------------------------------------------------
    # Core widget methods
    # -------------------------------------------------------------------------

    def place(self, cnf: dict[str, Any] | None = None, **kw: Unpack[PlaceKwargs]) -> Self:
        """Position this widget using the place geometry manager.

        Args:
            cnf: Optional dict of place options (same keys as `PlaceKwargs`).
            **kw: See `PlaceKwargs`.

        Returns:
            Self for method chaining.
        """
        options = cnf or {}
        options.update(kw)
        super().place(**options)  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def place_configure(self, cnf: dict[str, Any] | None = None, **kw: Unpack[PlaceKwargs]) -> Self:
        """Alias for `place()`.

        Args:
            cnf: Optional dict of place options.
            **kw: See `PlaceKwargs`.

        Returns:
            Self for method chaining.
        """
        return self.place(cnf, **kw)

    def place_forget(self) -> Self:
        """Unmap this widget and forget its place configuration.

        Returns:
            Self for method chaining.
        """
        super().place_forget()  # type: ignore[misc]
        return self  # type: ignore[return-value]

    def place_info(self) -> dict[str, Any]:
        """Return this widget's current place configuration.

        Returns:
            A dict containing the current place options for this widget
            (x, y, relx, rely, width, height, etc.).
        """
        return super().place_info()  # type: ignore[misc]

    # -------------------------------------------------------------------------
    # Container methods
    # -------------------------------------------------------------------------

    def place_slaves(self) -> list[Any]:
        """Return the widgets managed by place in this container.

        Returns:
            A list of child widgets managed by place.
        """
        return super().place_slaves()  # type: ignore[misc]
