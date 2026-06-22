from __future__ import annotations

from typing import Any, Callable

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

    There are two ways to use it:

    - **Figure host** — pass a ``figure`` you built. The chart embeds it and
      recolors its chrome to the theme. You own the figure; theming the data
      series is up to you.
    - **Managed render** — pass a ``render`` callback and (optionally) one or
      more ``signal`` objects. The chart owns the figure and redraws for you:
      each redraw clears the axes, applies the theme as matplotlib settings —
      including a semantic accent color cycle so multiple series are on-brand —
      then calls your ``render``. It re-renders when the theme changes or a bound
      signal updates::

          count = bs.Signal(20)
          def render(ax, n):
              ax.plot(range(n), [i * i for i in range(n)])
          bs.Chart(render=render, signal=count)   # redraws when `count` changes

    Args:
        figure: The matplotlib `Figure` to display (figure-host mode). Omit to
            start empty, or when using ``render``.
        render: A drawing callback for managed mode, called as ``render(ax)`` or
            ``render(ax, data)`` where `data` is the bound signal value(s). The
            chart clears and re-themes the axes before each call, so just draw.
        signal: A `bootstack.Signal` (or a list of them) whose value is passed to
            ``render`` as `data`; the chart re-renders when it changes. Requires
            ``render``.
        debounce: Milliseconds to coalesce rapid signal changes before
            re-rendering. ``0`` (default) re-renders on every change.
        parent: Explicit parent widget. If omitted, the current context-stack
            container is used.
        **kwargs: Layout placement options applied by the parent container
            (e.g. `grow`, `horizontal`, `row`, `column`), plus container styling
            such as `surface` and `padding`. See :doc:`/tasks/layout`.
    """

    _internal_class = _InternalChart

    def __init__(
        self,
        figure: Any = None,
        *,
        render: Callable | None = None,
        signal: Any = None,
        debounce: int = 0,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        _require_matplotlib()

        if signal is None:
            signals: list[Any] = []
        elif isinstance(signal, (list, tuple)):
            signals = list(signal)
        else:
            signals = [signal]
        if signals and render is None:
            raise BootstackError("Chart(signal=...) requires render= to draw the signal value.")

        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)
        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "figure": figure,
            "render": render,
            "signals": signals,
            "debounce": debounce,
        }
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

    def animate(
        self,
        setup: Callable,
        update: Callable,
        *,
        interval: int = 30,
        frames: Any = None,
    ) -> "ChartAnimation":
        """Drive a smooth, high-performance animation via blitting.

        Unlike the managed ``render=`` path (which rebuilds the whole figure on
        each update — right for occasional data changes, but limited to ~30 fps),
        animation updates artists in place and redraws only them over a cached
        background, sustaining high frame rates.

        Args:
            setup: Called once with the themed `Axes`. Create your artists with
                initial or empty data and set FIXED axis limits — blitting needs
                stable axes — then return the artist, or a list of artists, to
                animate.
            update: Called every frame as ``update(value, artist)`` (or
                ``update(value)``), where `artist` is whatever `setup` returned.
                For a continuous animation (the default) `value` is the elapsed
                time in **seconds** since the animation started — drive motion by
                this and the apparent speed stays constant even when frame timing
                jitters. If you pass `frames`, `value` is the current frame value
                instead. Mutate the artist's data in place; do not create new
                artists or rescale the axes.
            interval: Target milliseconds between frames. Default 30 (~33 fps).
            frames: An iterable of frame values to step through fixed data, or
                None (default) for a continuous, time-driven animation.

        Returns:
            A `ChartAnimation` handle — call `stop()` / `start()` to control it.
            The animation stops automatically when the widget is destroyed.
        """
        self._internal.animate(setup, update, interval=interval, frames=frames)
        return ChartAnimation(self._internal)


class ChartAnimation:
    """Handle for a running `Chart` animation.

    Returned by `Chart.animate`. Use it to pause and resume the animation or
    query whether it is playing.

    The animation is also gated on visibility: it pauses automatically when the
    chart is hidden (a switched-away tab, a scrolled-off region, a minimized
    window) or fully covered by another window, and resumes when shown — so an
    off-screen chart on a dashboard costs nothing. `stop` / `start` set your
    intent on top of that gate.
    """

    def __init__(self, chart: Any) -> None:
        self._chart = chart

    def stop(self) -> None:
        """Pause the animation; the last drawn frame stays on screen."""
        self._chart._set_anim_wanted(False)

    def start(self) -> None:
        """Resume the animation (subject to the chart being visible)."""
        self._chart._set_anim_wanted(True)

    @property
    def running(self) -> bool:
        """Whether the animation is currently playing (wanted and visible)."""
        return bool(self._chart._anim_wanted and self._chart._anim_visible())