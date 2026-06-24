"""Shared constants and PIL helpers for Slider and RangeSlider."""
from __future__ import annotations

from PIL import Image, ImageDraw
from PIL.ImageTk import PhotoImage

# Focus-ring border thickness. Retired (0): the ring was never wired to an
# actual keyboard-focus style and its frozen color did not track theme changes,
# so it only ever showed as a stale 1-2px border. Kept as a named constant so
# the geometry math (`cross_size + HL * 2`) and the highlight kwargs stay valid.
HL = 0

HANDLE_SIZE = 22   # handle diameter (px) — matches slider-handle.png at standard DPI
TRACK_H = 6        # track height (px)

# Value badge geometry
BADGE_H = 22
BADGE_PAD_X = 8
BADGE_GAP = 5       # gap between badge bottom and handle top
BADGE_FONT_SIZE = 9

# Tick geometry
TICK_GAP = 4
MAJOR_TICK_H = 8
MINOR_TICK_H = 4
LABEL_GAP = 3
LABEL_FONT_SIZE = 9

# Keyboard step sizes
STEP = 1
STEP_LARGE = 10

# Keyboard focus ring (RangeSlider: a halo around the active handle)
FOCUS_RING_GAP = 2    # gap between the handle edge and the ring
FOCUS_RING_W = 2      # ring stroke width
HALO_PAD = FOCUS_RING_GAP + FOCUS_RING_W   # ring overhang beyond the handle,
                                           # reserved on every side so it can't clip


def _make_focus_ring(diameter: int, color: str, width: int = FOCUS_RING_W) -> PhotoImage:
    """Render a smooth anti-aliased ring (transparent center) as a PhotoImage —
    the keyboard focus halo drawn around the active handle.

    Drawn as a filled outer disc with the center punched out (an annulus) at 4x
    and LANCZOS-downsampled, which anti-aliases far better than a thin outline
    stroke at the target size.
    """
    scale = 4
    s = diameter * scale
    margin = scale                       # 1px transparent margin so the outer edge
                                         # isn't clipped at the image boundary
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([margin, margin, s - 1 - margin, s - 1 - margin], fill=color)
    inset = margin + width * scale       # ring thickness = width (post-downsample)
    d.ellipse([inset, inset, s - 1 - inset, s - 1 - inset], fill=(0, 0, 0, 0))
    return PhotoImage(image=img.resize((diameter, diameter), Image.Resampling.LANCZOS))


def _make_badge(width: int, height: int, bg_color: str) -> PhotoImage:
    """Render an anti-aliased pill badge background as a PhotoImage."""
    sw, sh = width * 2, height * 2
    r = sh // 2
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=r, fill=bg_color)
    return PhotoImage(image=img.resize((width, height), Image.Resampling.LANCZOS))


def _make_handle(fill_color: str, ring_color: str, border_color: str) -> PhotoImage:
    """Recolor the slider-handle asset and return a PhotoImage.

    Args:
        fill_color: Accent color for the handle center (magenta channel).
        ring_color: Surface color for the outer ring (white channel).
        border_color: Neutral stroke around the outer edge (black channel).
    """
    from bootstack.style.utility import recolor_element_image
    result = recolor_element_image(
        'slider_handle',
        white_color=ring_color,
        black_color=border_color,
        magenta_color=fill_color,
    )
    return result.image


def _make_track(
    track_w: int,
    track_h: int,
    fill_start: int,
    fill_end: int,
    trough_color: str,
    fill_color: str,
    *,
    vertical: bool = False,
) -> PhotoImage | None:
    """Render a slider track (trough + fill region) as a PhotoImage.

    When `vertical=True` the image is rotated 90° CCW so the fill region
    appears at the bottom of the returned (tall) image.
    """
    if track_w < 1:
        return None
    # Render at 2× for crisp anti-aliased edges, then LANCZOS-downsample
    scale = 2
    sw, sh = track_w * scale, track_h * scale
    r = sh // 2
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=r, fill=trough_color)
    fw = (fill_end - fill_start) * scale
    if fw >= 1:
        d.rounded_rectangle(
            [fill_start * scale, 0, min(fill_end * scale, sw) - 1, sh - 1],
            radius=r, fill=fill_color,
        )
    img = img.resize((track_w, track_h), Image.Resampling.LANCZOS)
    if vertical:
        img = img.rotate(90, expand=True)
    return PhotoImage(image=img)


def get_widget_bg(widget: object) -> str | None:
    """Return a widget's rendered background as a `#rrggbb` hex string.

    Tries `cget('background')` first (tk widgets), then falls back to the
    ttk Style lookup (ttk widgets). Returns `None` when neither works.
    """
    if widget is None:
        return None
    # tk.Frame, tk.Canvas, etc. — direct option
    try:
        raw = widget.cget('background')  # type: ignore[union-attr]
        if raw:
            r, g, b = widget.winfo_rgb(raw)  # type: ignore[union-attr]
            return f"#{r // 256:02x}{g // 256:02x}{b // 256:02x}"
    except Exception:
        pass
    # ttk.Frame and bootstack Frame — resolve via style system
    try:
        from tkinter import ttk
        sname = widget.cget('style') or ''  # type: ignore[union-attr]
        style = ttk.Style(widget)  # type: ignore[arg-type]
        bg = style.lookup(sname, 'background') if sname else None
        if not bg:
            wclass = widget.winfo_class()  # type: ignore[union-attr]
            bg = style.lookup(wclass, 'background')
        if bg:
            r, g, b = widget.winfo_rgb(bg)  # type: ignore[union-attr]
            return f"#{r // 256:02x}{g // 256:02x}{b // 256:02x}"
    except Exception:
        pass
    return None


def resolve_colors(accent: str, surface: str, bg_override: str | None = None) -> dict[str, str]:
    """Resolve all slider colors from theme tokens.

    Args:
        accent: Accent token (e.g., `'primary'`, `'success'`).
        surface: Surface token (e.g., `'content'`, `'card'`).
        bg_override: Explicit hex background color (`'#rrggbb'`) to use
            instead of the theme default. Pass the result of
            `get_widget_bg(master)` to make the slider blend with its
            container surface.

    Returns:
        Dict of resolved hex color strings.
    """
    from bootstack.style.style import get_style
    b = get_style().style_builder
    bg = bg_override or b.color('background')
    accent_hex = b.color(accent)
    border = b.border(bg)
    # A muted tone with guaranteed ≥4.5 contrast against the slider's own surface.
    # (NOT `foreground[muted]`, which computes muted *relative to the foreground*
    # and so lands near the background — faint everywhere, invisible in e.g.
    # solarized-light. `muted_foreground(bg)` is the same value the public
    # `'muted'` token resolves to.)
    muted = b.muted_foreground(bg)
    return {
        'bg':              bg,
        'trough':          border,
        'fill':            accent_hex,
        'fill_disabled':   muted,
        'handle':          accent_hex,
        'handle_disabled': muted,
        'ring':            bg,
        'handle_border':   border,
        'badge_bg':        b.color('foreground'),
        'badge_text':      b.on_color(b.color('foreground')),
        'tick':            muted,
        'focus':           b.color('foreground'),
    }