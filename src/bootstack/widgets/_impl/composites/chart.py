"""Internal Chart composite — embeds a matplotlib figure in a themed frame.

Hosts a matplotlib ``FigureCanvasTkAgg`` inside a bootstack `Frame` and keeps the
figure's chrome colors (faces, spines, text) in sync with the active theme. The
public `bootstack.Chart` wrapper drives this; nothing here is public.

matplotlib is an optional dependency (the ``viz`` extra). It is imported lazily
inside the methods so that importing bootstack never pulls it in — only
constructing a `Chart` does.
"""

from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Master


def _theme_palette() -> dict[str, str]:
    """Resolve the chart's chrome colors from the active theme (best-effort)."""
    from bootstack.style import get_theme_color

    def color(token: str, fallback: str) -> str:
        try:
            return get_theme_color(token)
        except Exception:
            return fallback

    fg = color("foreground", "#212529")
    bg = color("background", "#ffffff")
    return {
        "figure_bg": bg,
        "axes_bg": color("content", bg),
        "fg": fg,
        "grid": color("stroke_subtle", fg),
    }


class Chart(Frame):
    """Frame hosting a matplotlib figure, recolored to match the theme."""

    def __init__(self, master: Master = None, *, figure: Any = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        self._figure = figure if figure is not None else Figure()
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._widget = self._canvas.get_tk_widget()
        self._widget.configure(highlightthickness=0, bd=0)
        self._widget.pack(fill="both", expand=True)

        self._style_figure()
        self._canvas.draw_idle()
        self._enable_theme_repaint(self._on_theme_changed)

    # ----- theme ------------------------------------------------------------

    def _style_figure(self) -> None:
        """Recolor the figure's chrome (faces, spines, text) to the theme.

        Best-effort pass over the *existing* artists — it does not impose a grid
        or restyle data series, which the figure's author owns. Never raises: a
        bespoke figure's quirks must not break the embed.
        """
        pal = _theme_palette()
        fig = self._figure
        try:
            fig.set_facecolor(pal["figure_bg"])
            for ax in fig.axes:
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
        except Exception:
            pass

    def _on_theme_changed(self) -> None:
        """Re-resolve theme colors and redraw (called after a theme rebuild)."""
        self._style_figure()
        try:
            self._canvas.draw_idle()
        except Exception:
            pass

    # ----- figure -----------------------------------------------------------

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
        self._style_figure()
        self._canvas.draw_idle()

    def draw(self) -> None:
        """Force a redraw of the current figure."""
        try:
            self._canvas.draw_idle()
        except Exception:
            pass