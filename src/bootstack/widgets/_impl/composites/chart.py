"""Internal Chart composite — embeds a matplotlib figure in a themed frame.

Two modes, both hosting a matplotlib ``FigureCanvasTkAgg`` inside a bootstack
`Frame`:

- **Figure host** (``figure=``): the caller owns a `Figure`; the composite embeds
  it and recolors its chrome (faces, spines, text) to the active theme — a
  best-effort pass over the existing artists.
- **Managed render** (``render=``): the composite owns the figure and redraw
  loop. Each redraw clears the axes, applies the theme as matplotlib rcParams
  (including a semantic accent color cycle), calls the caller's ``render(ax,
  data)``, and draws. It re-renders on theme change and whenever a bound
  `Signal` changes (optionally debounced).

The public `bootstack.Chart` wrapper drives this; nothing here is public.
matplotlib is an optional dependency (the ``viz`` extra), imported lazily inside
the methods so importing bootstack never pulls it in.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Sequence

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Master

# Accent roles used, in order, for the categorical series color cycle.
_CYCLE_ROLES = ("primary", "success", "info", "warning", "danger", "secondary")

# family name -> resolved family (or None if matplotlib can't find it). Cached so
# the theme-rc build does not probe the font manager on every redraw.
_FONT_CACHE: dict[str, str | None] = {}


def _color(token: str, fallback: str) -> str:
    """Resolve a theme color token to a hex string, falling back on failure."""
    from bootstack.style import get_theme_color

    try:
        return get_theme_color(token)
    except Exception:
        return fallback


def _resolve_font_family(name: str) -> str | None:
    """Return `name` if matplotlib can resolve that font family, else None."""
    if name in _FONT_CACHE:
        return _FONT_CACHE[name]
    resolved: str | None = None
    try:
        from matplotlib.font_manager import FontProperties, fontManager

        if fontManager.findfont(FontProperties(family=name), fallback_to_default=False):
            resolved = name
    except Exception:
        resolved = None
    _FONT_CACHE[name] = resolved
    return resolved


def _theme_palette() -> dict[str, str]:
    """The chart's chrome colors from the active theme (best-effort)."""
    fg = _color("foreground", "#212529")
    bg = _color("background", "#ffffff")
    return {
        "figure_bg": bg,
        "axes_bg": _color("content", bg),
        "fg": fg,
        "grid": _color("stroke_subtle", fg),
    }


def _theme_rc() -> dict[str, Any]:
    """Translate the active theme into a matplotlib rcParams dict.

    Governs artists created within a ``matplotlib.rc_context(rc)`` block: figure
    and axes faces, spine/tick/label/title colors, grid color, a semantic accent
    ``prop_cycle`` for series, and the theme body font.
    """
    pal = _theme_palette()
    fg = pal["fg"]
    rc: dict[str, Any] = {
        "figure.facecolor": pal["figure_bg"],
        "savefig.facecolor": pal["figure_bg"],
        "axes.facecolor": pal["axes_bg"],
        "axes.edgecolor": fg,
        "axes.labelcolor": fg,
        "axes.titlecolor": fg,
        "text.color": fg,
        "xtick.color": fg,
        "ytick.color": fg,
        "xtick.labelcolor": fg,
        "ytick.labelcolor": fg,
        "grid.color": pal["grid"],
        "legend.facecolor": pal["axes_bg"],
        "legend.edgecolor": fg,
    }

    cycle: list[str] = []
    for role in _CYCLE_ROLES:
        hexval = _color(f"{role}[500]", "") or _color(role, "")
        if hexval:
            cycle.append(hexval)
    if cycle:
        try:
            from cycler import cycler

            rc["axes.prop_cycle"] = cycler(color=cycle)
        except Exception:
            pass

    try:
        from bootstack.style.style import get_theme_provider

        spec = get_theme_provider().typography.body
        rc["font.size"] = spec.size
        family = _resolve_font_family(spec.font)
        if family:
            rc["font.family"] = family
    except Exception:
        pass

    return rc


def _positional_arity(fn: Callable) -> int:
    """Count the positional parameters of `fn` (``*args`` counts as 2)."""
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return 2
    params = sig.parameters.values()
    if any(p.kind == p.VAR_POSITIONAL for p in params):
        return 2
    return sum(
        1 for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    )


def _as_artist_list(result: Any) -> list[Any]:
    """Normalize a setup() return (one artist or several) to a list."""
    if result is None:
        return []
    if isinstance(result, (list, tuple)):
        return list(result)
    return [result]


class Chart(Frame):
    """Frame hosting a matplotlib figure — themed, optionally managed/reactive."""

    def __init__(
        self,
        master: Master = None,
        *,
        figure: Any = None,
        render: Callable | None = None,
        signals: Sequence[Any] | None = None,
        debounce: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        from bootstack.scheduling import Schedule

        self._render = render
        self._render_arity = _positional_arity(render) if render else 0
        self._signals = list(signals) if signals else []
        self._debounce = max(0, int(debounce))
        self._debounce_job: Any = None
        self._render_pending = False
        self._signal_handles: list[Any] = []
        self._schedule = Schedule(self)
        self._anim: Any = None  # matplotlib FuncAnimation when animate() is used
        self._anim_artists: list[Any] = []
        self._anim_wanted = False        # user intent: should it be playing
        self._anim_running_now = False   # actual timer state we last applied
        self._anim_obscured = False      # fully covered by another window
        self._anim_first_draw_cid: Any = None

        self._figure = figure if figure is not None else Figure()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._widget = self._canvas.get_tk_widget()
        self._widget.configure(highlightthickness=0, bd=0)
        self._widget.pack(fill="both", expand=True)

        if self._render is not None:
            self._render_managed()
        else:
            self._style_figure()
            self._canvas.draw_idle()

        self._enable_theme_repaint(self._on_theme_changed)
        self._bind_signals()
        # Visibility gating for animations: pause when the chart is hidden
        # (Map/Unmap — tabs, pages, minimized; reliable cross-platform) or fully
        # covered by another window (Visibility — best-effort, mainly X11).
        self.bind("<Map>", self._on_anim_visibility, add="+")
        self.bind("<Unmap>", self._on_anim_visibility, add="+")
        self.bind("<Visibility>", self._on_anim_obscured, add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")

    # ----- reactive wiring --------------------------------------------------

    def _bind_signals(self) -> None:
        for sig in self._signals:
            try:
                self._signal_handles.append(sig.subscribe(self._on_signal_change))
            except Exception:
                pass

    def _on_signal_change(self, *_: Any) -> None:
        if self._debounce > 0:
            if self._debounce_job is not None:
                try:
                    self._debounce_job.cancel()
                except Exception:
                    pass
            self._debounce_job = self._schedule.delay(self._debounce, self._request_render)
        else:
            self._request_render()

    def _request_render(self) -> None:
        """Coalesce a burst of changes into one render at the next idle frame.

        A timer or stream that updates a bound signal faster than matplotlib can
        draw would otherwise queue an unbounded backlog of synchronous rebuilds
        and starve the event loop. Collapsing to one render per idle keeps the UI
        responsive and the redraw rate bounded by what the figure can sustain.
        """
        if self._render_pending or not self.winfo_exists():
            return
        self._render_pending = True
        self._schedule.idle(self._flush_render)

    def _flush_render(self) -> None:
        self._render_pending = False
        self._render_managed()

    def _current_data(self) -> Any:
        """The data passed to a managed render — a signal value, a tuple of
        values for multiple signals, or None when no signal is bound.
        """
        if not self._signals:
            return None
        values = [sig() for sig in self._signals]
        return values[0] if len(values) == 1 else tuple(values)

    # ----- managed render ---------------------------------------------------

    def _render_managed(self) -> None:
        """Clear, apply the theme rc, call the caller's render, and draw."""
        if self._render is None or not self.winfo_exists():
            return
        import matplotlib

        rc = _theme_rc()
        fig = self._figure
        fig.clear()
        fig.set_facecolor(rc["figure.facecolor"])
        data = self._current_data()
        with matplotlib.rc_context(rc):
            ax = fig.add_subplot(111)
            if self._render_arity >= 2:
                self._render(ax, data)
            else:
                self._render(ax)
        self._canvas.draw_idle()

    # ----- figure-host theming ----------------------------------------------

    def _style_figure(self) -> None:
        """Recolor an externally-built figure's chrome to the theme.

        Best-effort pass over the *existing* artists — it does not impose a grid
        or restyle data series, which the figure's author owns. Never raises.
        """
        pal = _theme_palette()
        fig = self._figure
        try:
            fig.set_facecolor(pal["figure_bg"])
            for ax in fig.axes:
                self._recolor_axes(ax, pal)
        except Exception:
            pass

    @staticmethod
    def _recolor_axes(ax: Any, pal: dict[str, str]) -> None:
        """Recolor one axes' chrome (faces, spines, ticks, labels) to the theme."""
        ax.set_facecolor(pal["axes_bg"])
        for spine in ax.spines.values():
            spine.set_color(pal["fg"])
        ax.tick_params(colors=pal["fg"], which="both")
        ax.xaxis.label.set_color(pal["fg"])
        ax.yaxis.label.set_color(pal["fg"])
        ax.title.set_color(pal["fg"])
        for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
            label.set_color(pal["fg"])
        for line in (*ax.get_xgridlines(), *ax.get_ygridlines()):
            line.set_color(pal["grid"])
        legend = ax.get_legend()
        if legend is not None:
            frame = legend.get_frame()
            frame.set_facecolor(pal["axes_bg"])
            frame.set_edgecolor(pal["fg"])
            for text in legend.get_texts():
                text.set_color(pal["fg"])

    def _on_theme_changed(self) -> None:
        """Re-resolve theme colors and redraw (called after a theme rebuild)."""
        if self._anim is not None:
            # Recolor the axes chrome, then force the animation to recapture its
            # blit background in the new theme. The blit cache only re-grabs when
            # the axes *view* changes, so a recolor alone would keep restoring the
            # stale background over the new colors — clearing the cache forces a
            # fresh grab on the next frame. Animated artists keep their setup
            # colors. (Falls back to a plain draw if matplotlib internals shift.)
            pal = _theme_palette()
            try:
                self._figure.set_facecolor(pal["figure_bg"])
                for ax in self._figure.axes:
                    self._recolor_axes(ax, pal)
                self._canvas.draw()  # render the new-colored background to the buffer
                cache = getattr(self._anim, "_blit_cache", None)
                if cache is not None:
                    cache.clear()  # next frame re-grabs the background
            except Exception:
                try:
                    self._canvas.draw()
                except Exception:
                    pass
        elif self._render is not None:
            self._render_managed()  # full re-render picks up the new rc + cycle
        else:
            self._style_figure()
            try:
                self._canvas.draw_idle()
            except Exception:
                pass

    # ----- figure / lifecycle -----------------------------------------------

    def set_figure(self, figure: Any) -> None:
        """Replace the embedded figure, tearing down the old canvas widget."""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        if figure is None:
            figure = Figure()
        if self._widget is not None:
            self._widget.destroy()
        self._figure = figure
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._widget = self._canvas.get_tk_widget()
        self._widget.configure(highlightthickness=0, bd=0)
        self._widget.pack(fill="both", expand=True)
        if self._render is not None:
            self._render_managed()
        else:
            self._style_figure()
            self._canvas.draw_idle()

    def draw(self) -> None:
        """Redraw — re-run the managed render, or refresh the hosted figure."""
        if self._render is not None:
            self._render_managed()
        else:
            try:
                self._canvas.draw_idle()
            except Exception:
                pass

    # ----- animation (blitting) ---------------------------------------------

    def animate(
        self,
        setup: Callable,
        update: Callable,
        *,
        interval: int = 30,
        frames: Any = None,
    ) -> Any:
        """Drive a blitting animation, returning the matplotlib animation object.

        Owns the figure: clears it, builds a themed axes, calls ``setup(ax)``
        once to create the artists, then each frame calls ``update(value,
        artists)`` and redraws only those artists over a cached background.
        `value` is elapsed seconds for a continuous animation (so motion is
        time-based and jitter-free), or the frame value when `frames` is given.
        """
        import itertools
        import time

        import matplotlib
        from matplotlib.animation import FuncAnimation

        self._stop_anim()
        update_arity = _positional_arity(update)
        # Continuous animation (no explicit `frames`) is driven by elapsed
        # wall-clock time, not the frame index — so uneven timer delivery does
        # not change the apparent velocity (no speed-up / slow-down jitter).
        timed = frames is None
        start = {"t": None}

        rc = _theme_rc()
        fig = self._figure
        fig.clear()
        fig.set_facecolor(rc["figure.facecolor"])
        with matplotlib.rc_context(rc):
            ax = fig.add_subplot(111)
            # Create the artists ONCE. FuncAnimation re-invokes init_func on every
            # full redraw (resize/theme), so init must only RETURN the artists —
            # re-running setup there would accumulate a new artist each redraw.
            self._anim_artists = _as_artist_list(setup(ax))

        def init() -> list[Any]:
            return self._anim_artists

        def func(frame: Any) -> list[Any]:
            artists = self._anim_artists
            arg = artists[0] if len(artists) == 1 else artists
            if timed:
                if start["t"] is None:
                    start["t"] = time.perf_counter()
                value: Any = time.perf_counter() - start["t"]
            else:
                value = frame
            if update_arity >= 2:
                update(value, arg)
            else:
                update(value)
            return self._anim_artists

        self._anim = FuncAnimation(
            fig,
            func,
            init_func=init,
            frames=frames if frames is not None else itertools.count(),
            interval=max(1, int(interval)),
            blit=True,
            cache_frame_data=False,
        )
        self._anim_wanted = True
        self._anim_obscured = False
        # FuncAnimation auto-starts on the first draw_event; assume running, then
        # reconcile against actual visibility once that first draw has happened
        # (covers a chart created on a hidden tab).
        self._anim_running_now = True

        def _after_first_draw(_event: Any) -> None:
            if self._anim_first_draw_cid is not None:
                try:
                    self._canvas.mpl_disconnect(self._anim_first_draw_cid)
                except Exception:
                    pass
                self._anim_first_draw_cid = None
            self._apply_anim_state()

        self._anim_first_draw_cid = self._canvas.mpl_connect("draw_event", _after_first_draw)
        self._canvas.draw_idle()
        return self._anim

    def _anim_visible(self) -> bool:
        """Whether the chart is actually visible — mapped and not fully covered."""
        try:
            return bool(self.winfo_viewable()) and not self._anim_obscured
        except Exception:
            return not self._anim_obscured

    def _apply_anim_state(self) -> None:
        """Run the animation only when wanted AND actually visible."""
        anim = self._anim
        if anim is None:
            return
        should = self._anim_wanted and self._anim_visible()
        if should == self._anim_running_now:
            return
        try:
            anim.resume() if should else anim.pause()
        except Exception:
            return
        self._anim_running_now = should

    def _set_anim_wanted(self, wanted: bool) -> None:
        self._anim_wanted = bool(wanted)
        self._apply_anim_state()

    def _on_anim_visibility(self, event: Any = None) -> None:
        if event is not None and getattr(event, "widget", None) is not self:
            return
        if self._anim is not None:
            self._apply_anim_state()

    def _on_anim_obscured(self, event: Any = None) -> None:
        # `<Visibility>` is best-effort (mainly X11); only a FULL cover pauses.
        state = getattr(event, "state", "") if event is not None else ""
        self._anim_obscured = state == "VisibilityFullyObscured"
        if self._anim is not None:
            self._apply_anim_state()

    def _stop_anim(self) -> None:
        anim = self._anim
        self._anim = None
        self._anim_wanted = False
        self._anim_running_now = False
        if self._anim_first_draw_cid is not None:
            try:
                self._canvas.mpl_disconnect(self._anim_first_draw_cid)
            except Exception:
                pass
            self._anim_first_draw_cid = None
        if anim is not None:
            try:
                anim.event_source.stop()
            except Exception:
                pass

    def _on_destroy(self, event: Any = None) -> None:
        if event is not None and getattr(event, "widget", None) is not self:
            return
        self._stop_anim()
        for handle in self._signal_handles:
            try:
                handle.cancel()
            except Exception:
                pass
        self._signal_handles = []
        if self._debounce_job is not None:
            try:
                self._debounce_job.cancel()
            except Exception:
                pass
            self._debounce_job = None