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

# Standard navigation tools: name -> (icon glyph, group). The group index drives
# the auto-inserted divider between adjacent tools of different groups (history /
# navigate / io). `toolbar=True` renders them all, in this order.
_TOOL_ICONS = {
    "home": "house",
    "back": "arrow-left",
    "forward": "arrow-right",
    "pan": "arrows-move",
    "zoom": "zoom-in",
    "save": "download",
}
_TOOL_GROUP = {"home": 0, "back": 0, "forward": 0, "pan": 1, "zoom": 1, "save": 2}
_DEFAULT_TOOLS = ("home", "back", "forward", "pan", "zoom", "save")

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


def _accent_cycle() -> list[str]:
    """The categorical series colors from the active theme's accent roles."""
    cycle: list[str] = []
    for role in _CYCLE_ROLES:
        hexval = _color(f"{role}[500]", "") or _color(role, "")
        if hexval:
            cycle.append(hexval)
    return cycle


# seaborn runs lower-saturation than matplotlib (its plots are usually
# area-filled — bars, violins, KDE — where vivid blocks read heavy). We keep the
# brand hues but soften them to match the seaborn aesthetic, via seaborn's own
# `desat`. matplotlib line plots keep the full-saturation `[500]` cycle.
_SEABORN_DESAT = 0.75


def _seed_seaborn(cycle: list[str], desat: float = _SEABORN_DESAT) -> None:
    """If seaborn is already imported, point its palette at the accent cycle.

    A no-op when seaborn is not in use — the composite never imports it (it stays
    in the optional ``viz-seaborn`` extra, off the import path). When the user has
    imported seaborn, this is what makes a `sns.barplot(..., ax=ax)` (or any
    categorical seaborn plot) pick up the theme's accent colors instead of
    seaborn's own default palette — softened by `desat` to suit seaborn's muted,
    fill-heavy look. Called inside the render `rc_context`, so it governs that
    render and reverts with the rest of the themed rcParams.
    """
    import sys

    sns = sys.modules.get("seaborn")
    if sns is None or not cycle:
        return
    try:
        sns.set_palette(sns.color_palette(cycle, desat=desat))
    except Exception:
        pass


def _theme_rc(with_cycle: bool = True) -> dict[str, Any]:
    """Translate the active theme into a matplotlib rcParams dict.

    Governs artists created within a ``matplotlib.rc_context(rc)`` block: figure
    and axes faces, spine/tick/label/title colors, grid color, the theme body
    font, and — when `with_cycle` is true — a semantic accent ``prop_cycle`` for
    series. The chrome keys are always present; only the series color cycle is
    optional, so ``themed=False`` keeps the chart fitting the app while leaving
    data colors to the caller.
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

    cycle = _accent_cycle() if with_cycle else []
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
        data_source: Any = None,
        debounce: int = 0,
        toolbar: bool | Sequence[str] = False,
        themed: bool = True,
        seaborn_desat: float = _SEABORN_DESAT,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        from matplotlib.figure import Figure

        from bootstack.scheduling import Schedule

        self._themed = bool(themed)
        self._seaborn_desat = float(seaborn_desat)
        self._render = render
        self._render_arity = _positional_arity(render) if render else 0
        self._signals = list(signals) if signals else []
        self._data_source = data_source
        self._rows: list[Any] = []
        self._source_handle: Any = None
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

        # Navigation toolbar. `_nav` is matplotlib's logic-only
        # NavigationToolbar2Tk; `_navbar` is the themed bootstack bar that drives
        # it. Built per-canvas in `_build_canvas` so a figure swap rebuilds both.
        # `toolbar` selects the standard tools: True = all, a sequence = that
        # subset (in order), False = no bar. An empty sequence builds an empty bar
        # for author-only buttons via `chart.toolbar`.
        if toolbar is False or toolbar is None:
            self._toolbar_tools: list[str] | None = None
        elif toolbar is True:
            self._toolbar_tools = list(_DEFAULT_TOOLS)
        else:
            self._toolbar_tools = list(toolbar)
        if self._toolbar_tools:
            from bootstack.errors import BootstackError

            unknown = [t for t in self._toolbar_tools if t not in _TOOL_ICONS]
            if unknown:
                raise BootstackError(
                    f"Chart(toolbar=) has unknown tool(s) {unknown}; valid tools "
                    f"are {list(_TOOL_ICONS)}."
                )
        self._show_toolbar = self._toolbar_tools is not None
        self._canvas: Any = None
        self._widget: Any = None
        self._nav: Any = None
        self._navbar: Any = None
        self._navdiv: Any = None
        self._pan_btn: Any = None
        self._zoom_btn: Any = None
        self._msg_label: Any = None

        self._figure = figure if figure is not None else Figure()
        self._build_canvas()

        # Bind a data source before the first render so its rows are available.
        if self._data_source is not None:
            self._rows = self._read_rows()
            try:
                self._source_handle = self._data_source.on_change(self._on_source_change)
            except Exception:
                self._source_handle = None

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

    # ----- canvas + navigation toolbar --------------------------------------

    def _build_canvas(self) -> None:
        """Embed the current figure, with the themed nav toolbar when enabled."""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._widget = self._canvas.get_tk_widget()
        self._widget.configure(highlightthickness=0, bd=0)
        if self._show_toolbar:
            self._build_navbar()  # packs at the top, above the canvas
        self._widget.pack(fill="both", expand=True)

    def _teardown_canvas(self) -> None:
        """Destroy the canvas and toolbar (for a figure swap)."""
        self._pan_btn = self._zoom_btn = self._msg_label = None
        for attr in ("_navbar", "_navdiv", "_nav", "_widget"):
            widget = getattr(self, attr, None)
            if widget is not None:
                try:
                    widget.destroy()
                except Exception:
                    pass
            setattr(self, attr, None)
        self._canvas = None

    def _build_navbar(self) -> None:
        """Build a themed bootstack toolbar driving matplotlib's navigation.

        matplotlib splits navigation *logic* (history, pan, zoom-rectangle, the
        canvas-drawn rubber band) from its raw-Tk button strip. We instantiate
        `NavigationToolbar2Tk` with ``pack_toolbar=False`` so its unstyled tk
        frame is created but never mapped, then wire a compact bootstack bar to
        its methods — reusing the pan/zoom math and rubber band with zero
        reimplementation, and none of the off-theme tk chrome.
        """
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

        from bootstack.widgets._impl.composites.toolbar import Toolbar as _Toolbar

        from bootstack.widgets._impl.primitives.label import Label
        from bootstack.widgets._impl.primitives.separator import Separator

        self._nav = NavigationToolbar2Tk(self._canvas, self, pack_toolbar=False)
        # Route matplotlib's coordinate readout to our themed label.
        self._nav.set_message = self._set_nav_message

        # The bar blends into the chart surface; a soft hairline below it (the
        # shell chrome-divider strength) separates it from the canvas, instead of
        # a tinted band.
        commands = {
            "home": self._nav.home,
            "back": self._nav.back,
            "forward": self._nav.forward,
            "pan": self._toggle_pan,
            "zoom": self._toggle_zoom,
            "save": self._save_figure,
        }
        bar = _Toolbar(self, density="compact")
        prev_group: int | None = None
        for name in self._toolbar_tools or ():
            # A divider falls between adjacent tools of different groups.
            if prev_group is not None and _TOOL_GROUP[name] != prev_group:
                bar.add_separator()
            btn = bar.add_button(icon=_TOOL_ICONS[name], command=commands[name])
            if name == "pan":
                self._pan_btn = btn
            elif name == "zoom":
                self._zoom_btn = btn
            prev_group = _TOOL_GROUP[name]
        # The coordinate readout anchors to the right edge; author-added buttons
        # pack to the left (after the built-in tools), so the two never collide.
        self._msg_label = Label(bar.content, text="", font="caption")
        self._msg_label.pack(side="right", padx=6)
        bar.pack(side="top", fill="x")
        divider = Separator(self, orient="horizontal", border_strength=0.90)
        divider.pack(side="top", fill="x")
        self._navbar = bar
        self._navdiv = divider

    def _toggle_pan(self) -> None:
        if self._nav is not None:
            self._nav.pan()
            self._sync_nav_modes()

    def _toggle_zoom(self) -> None:
        if self._nav is not None:
            self._nav.zoom()
            self._sync_nav_modes()

    def _sync_nav_modes(self) -> None:
        """Reflect the active pan/zoom mode in the toolbar buttons."""
        mode = str(getattr(self._nav, "mode", ""))
        self._set_button_active(self._pan_btn, mode == "pan/zoom")
        self._set_button_active(self._zoom_btn, mode == "zoom rect")

    @staticmethod
    def _set_button_active(btn: Any, active: bool) -> None:
        if btn is None:
            return
        try:
            if active:
                btn.configure(variant="solid", accent="primary")
            else:
                btn.configure(variant="ghost", accent="")
        except Exception:
            pass

    def _set_nav_message(self, text: str) -> None:
        if self._msg_label is not None:
            try:
                self._msg_label.configure(text=text or "")
            except Exception:
                pass

    def _save_figure(self) -> None:
        """Save the figure through bootstack's themed file dialog."""
        from bootstack.dialogs import ask_save_file

        path = ask_save_file(
            title="Save chart",
            initial_file="chart.png",
            file_types=[
                ("PNG image", "*.png"),
                ("PDF document", "*.pdf"),
                ("SVG image", "*.svg"),
                ("All files", "*.*"),
            ],
            default_extension=".png",
            parent=self,
        )
        if path:
            try:
                self._figure.savefig(path)
            except Exception:
                pass

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
        """The data passed to a managed render.

        The bound data source's rows when one is set; otherwise a signal value
        (or a tuple of values for multiple signals); or None.
        """
        if self._data_source is not None:
            return self._rows
        if not self._signals:
            return None
        values = [sig() for sig in self._signals]
        return values[0] if len(values) == 1 else tuple(values)

    # ----- data source ------------------------------------------------------

    def _read_rows(self) -> list[Any]:
        """Read all current records from the source (respecting its filter/sort)."""
        ds = self._data_source
        if ds is None:
            return []
        try:
            n = ds.count
            return list(ds.page_slice(0, n)) if n else []
        except Exception:
            return []

    def _on_source_change(self, _event: Any = None) -> None:
        self._rows = self._read_rows()
        self._request_render()

    # ----- managed render ---------------------------------------------------

    def _invoke_render(self, ax: Any, data: Any) -> None:
        if self._render_arity >= 2:
            self._render(ax, data)
        else:
            self._render(ax)

    def _render_managed(self) -> None:
        """Clear, apply the theme rc, call render, and draw.

        The chrome (backgrounds, text, axes) is always themed so the chart fits
        the app. ``themed=False`` only drops the accent series cycle and seaborn
        palette, leaving data colors to the caller; explicit per-series colors win
        either way. Reactivity is unchanged.
        """
        if self._render is None or not self.winfo_exists():
            return
        import matplotlib

        rc = _theme_rc(with_cycle=self._themed)
        fig = self._figure
        fig.clear()
        fig.set_facecolor(rc["figure.facecolor"])
        data = self._current_data()
        with matplotlib.rc_context(rc):
            if self._themed:
                _seed_seaborn(_accent_cycle(), self._seaborn_desat)
            self._invoke_render(fig.add_subplot(111), data)
        self._canvas.draw_idle()

    # ----- figure-host theming ----------------------------------------------

    def _style_figure(self) -> None:
        """Recolor an externally-built figure's chrome to the theme.

        Best-effort pass over the *existing* artists — it does not impose a grid
        or restyle data series, which the figure's author owns. Never raises. The
        chrome always tracks the theme (independent of ``themed=``, which only
        governs whether the managed path imposes the accent series colors).
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
        """Re-resolve theme colors and redraw (called after a theme rebuild).

        Runs regardless of ``themed=`` — the chrome always follows the theme so
        the chart keeps fitting the app; ``themed=False`` only drops the accent
        series colors, which a re-render naturally honors.
        """
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
        from matplotlib.figure import Figure

        if figure is None:
            figure = Figure()
        self._teardown_canvas()
        self._figure = figure
        self._build_canvas()
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

        rc = _theme_rc(with_cycle=self._themed)
        fig = self._figure
        fig.clear()
        fig.set_facecolor(rc["figure.facecolor"])
        # Create the artists ONCE. FuncAnimation re-invokes init_func on every
        # full redraw (resize/theme), so init must only RETURN the artists —
        # re-running setup there would accumulate a new artist each redraw.
        with matplotlib.rc_context(rc):
            if self._themed:
                _seed_seaborn(_accent_cycle(), self._seaborn_desat)
            self._anim_artists = _as_artist_list(setup(fig.add_subplot(111)))

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
        if self._source_handle is not None:
            try:
                self._source_handle.cancel()
            except Exception:
                pass
            self._source_handle = None
        if self._debounce_job is not None:
            try:
                self._debounce_job.cancel()
            except Exception:
                pass
            self._debounce_job = None