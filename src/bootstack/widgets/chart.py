from __future__ import annotations

from typing import Any

from bootstack.errors import BootstackError
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._impl.composites.chart import Chart as _InternalChart


def _require_matplotlib() -> None:
    """Raise a friendly error if the optional matplotlib dependency is missing."""
    try:
        import matplotlib  # noqa: F401
    except ImportError as exc:
        raise BootstackError(
            "Chart requires matplotlib, which is not installed. Install the "
            "optional visualization extra with:\n\n    pip install bootstack[viz]"
        ) from exc


class Chart(PublicWidgetBase):
    """Embed a matplotlib figure in a bootstack app, themed to match.

    `Chart` is the bridge between bootstack and the scientific Python plotting
    stack. You build a plot with matplotlib (or seaborn, which draws onto the
    same axes) and hand the figure to a `Chart`; it embeds the figure as a
    first-class widget that fills its space and recolors its chrome — figure and
    axes backgrounds, spines, ticks, and text — to match the active theme,
    flipping with light/dark like everything else in the app.

    `Chart` is deliberately not a plotting API: it does not wrap matplotlib's
    drawing calls. You keep the full expressive power of matplotlib/seaborn and
    bootstack owns only the embedding, theming, and redraw.

    matplotlib is an optional dependency. Install it with the visualization
    extra: ``pip install bootstack[viz]`` (or ``bootstack[viz-seaborn]`` to add
    seaborn). Constructing a `Chart` without matplotlib installed raises a
    `bootstack.errors.BootstackError` explaining how to install it.

    Build the figure with matplotlib's object API (``matplotlib.figure.Figure``)
    rather than ``pyplot`` — an embedded figure must be a standalone object, and
    ``pyplot`` would also open a separate window.

    Args:
        figure: The matplotlib `Figure` to display. Omit to start with an empty
            figure you populate later via the `ax` accessor or the `figure`
            property.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container
            (e.g. `grow`, `horizontal`, `row`, `column`), plus container styling
            such as `surface` and `padding`. See :doc:`/tasks/layout`.
    """

    _internal_class = _InternalChart

    def __init__(self, figure: Any = None, *, parent: Any = None, **kwargs: Any) -> None:
        _require_matplotlib()
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"figure": figure}
        internal_kwargs.update(kwargs)
        self._internal = self._internal_class(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def figure(self) -> Any:
        """The embedded matplotlib `Figure`.

        Assign a new `Figure` to swap what is displayed; the old canvas is torn
        down and the new figure is themed and drawn.
        """
        return self._internal._figure

    @figure.setter
    def figure(self, value: Any) -> None:
        self._internal.set_figure(value)

    @property
    def ax(self) -> Any:
        """The figure's primary `Axes`, creating one if the figure is empty.

        A convenience for the common single-plot case::

            chart = bs.Chart()
            chart.ax.plot([1, 2, 3])
            chart.draw()
        """
        fig = self._internal._figure
        return fig.axes[0] if fig.axes else fig.add_subplot(111)

    # ----- Methods -----

    def draw(self) -> None:
        """Redraw the figure after mutating it in place.

        Call this after drawing onto `ax` (or the figure) so the change appears.
        Theme changes redraw automatically — this is for your own updates.
        """
        self._internal.draw()