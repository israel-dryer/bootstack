"""Internal Avatar composite — a small identity badge.

Shows either an image (cover-fit, clipped to the avatar shape) or initials on a
filled tile. Canvas-backed: the image path reuses the shared `_image_fit`
helpers, and initials are drawn as Tk canvas text (so they use the framework's
fonts cross-platform — PIL has no bundled text font). The public
`bootstack.Avatar` wrapper drives this.
"""

from __future__ import annotations

from tkinter import Canvas, TclError
from typing import Any, Literal

from PIL import Image as PILImage, ImageDraw
from PIL.Image import Resampling
from PIL.ImageTk import PhotoImage

from bootstack.style.style import get_style
from bootstack.widgets._impl.composites._image_fit import fit_image, resolve_pil, round_corners
from bootstack.widgets._impl.primitives.frame import Frame
from bootstack.widgets.types import Master

Shape = Literal["circle", "rounded", "square"]


def _initials_from(name: str | None, initials: str | None) -> str:
    """Resolve the initials to show: explicit override, else derived from `name`."""
    if initials:
        return initials.strip()[:2].upper()
    if name:
        parts = [p for p in name.split() if p]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
    return ""


class Avatar(Frame):
    """Canvas-backed avatar — an image or initials on a filled tile."""

    def __init__(
        self,
        master: Master = None,
        *,
        source: Any = None,
        name: str | None = None,
        initials: str | None = None,
        size: int = 40,
        shape: Shape = "circle",
        background: str = "primary",
        foreground: str = "white",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._size = max(8, int(size))
        self._shape: Shape = shape
        self._background = background
        self._foreground = foreground
        self._source = source
        self._name = name
        self._initials = initials
        self._photo: PhotoImage | None = None   # strong ref (Tk GC)

        self._canvas = Canvas(self, width=self._size, height=self._size,
                              highlightthickness=0, bd=0,
                              background=self._surface_color())
        self._canvas.pack()
        self._canvas.bind("<Button-1>", self._forward_click)
        self.bind("<<BsThemeChanged>>", self._on_theme, add="+")

        self._render()

    # ----- helpers -----------------------------------------------------------

    def _surface_color(self) -> str:
        token = getattr(self, "_surface", None) or "background"
        b = get_style().style_builder
        try:
            return b.color(token)
        except Exception:
            return b.color("background")

    def _color(self, token: str) -> str:
        try:
            return get_style().style_builder.color(token)
        except Exception:
            return token

    def _radius(self) -> int:
        if self._shape == "circle":
            return self._size // 2
        if self._shape == "rounded":
            return max(1, int(self._size * 0.25))
        return 0

    # ----- rendering ---------------------------------------------------------

    def _render(self) -> None:
        self._canvas.delete("all")
        pil = resolve_pil(self._source) if self._source is not None else None
        if pil is not None:
            self._render_image(pil)
        else:
            self._render_initials()

    def _render_image(self, pil: PILImage.Image) -> None:
        composed = fit_image(pil.convert("RGBA"), self._size, self._size, "cover")
        radius = self._radius()
        if radius > 0:
            composed = round_corners(composed, radius)
        self._photo = PhotoImage(composed)
        self._canvas.create_image(self._size // 2, self._size // 2,
                                  image=self._photo, anchor="center")

    def _render_initials(self) -> None:
        # Filled tile (antialiased) in the background color, clipped to the shape.
        ss = 4
        s = self._size
        big = PILImage.new("RGBA", (s * ss, s * ss), (0, 0, 0, 0))
        fill = _hex_or_name_to_rgba(self._color(self._background))
        ImageDraw.Draw(big).rounded_rectangle(
            [0, 0, s * ss - 1, s * ss - 1], radius=self._radius() * ss, fill=fill
        )
        self._photo = PhotoImage(big.resize((s, s), Resampling.LANCZOS))
        self._canvas.create_image(s // 2, s // 2, image=self._photo, anchor="center")

        text = _initials_from(self._name, self._initials)
        if text:
            font_size = max(8, int(s * 0.4))
            self._canvas.create_text(
                s // 2, s // 2, text=text, fill=self._text_color(),
                font=(self._ui_family(), font_size, "bold"), anchor="center",
            )

    def _text_color(self) -> str:
        """The resolved foreground color, validated as a Tk color (else white)."""
        color = self._color(self._foreground)
        try:
            self._canvas.winfo_rgb(color)   # authoritative Tk color parse
            return color
        except TclError:
            return "#ffffff"

    @staticmethod
    def _ui_family() -> str:
        """The framework's configured UI font family.

        bootstack overrides `TkDefaultFont` to its body font, so reading its
        actual family gives the app's UI font for the initials text.
        """
        from tkinter import font as tkfont

        try:
            return tkfont.nametofont("TkDefaultFont").actual("family")
        except Exception:
            return ""

    def _on_theme(self, _event=None) -> None:
        try:
            self._canvas.configure(background=self._surface_color())
        except TclError:
            return
        self._render()

    def _forward_click(self, event) -> None:
        self.event_generate("<<AvatarClick>>", x=event.x, y=event.y)

    # ----- live updates ------------------------------------------------------

    def set_source(self, source: Any) -> None:
        self._source = source
        self._render()

    def set_text(self, *, name: str | None = None, initials: str | None = None) -> None:
        self._name = name
        self._initials = initials
        self._render()


def _hex_or_name_to_rgba(color: str) -> tuple[int, int, int, int]:
    """Parse a resolved color (hex or name) to an opaque RGBA tuple for PIL fill."""
    from PIL import ImageColor

    try:
        r, g, b = ImageColor.getrgb(color)[:3]
        return (r, g, b, 255)
    except (ValueError, TypeError):
        return (108, 117, 125, 255)   # neutral gray fallback
