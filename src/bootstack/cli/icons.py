"""Icons command — launches the Bootstrap Icons browser."""
from __future__ import annotations

import argparse
import sys
from typing import Any


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "icons",
        help="Browse Bootstrap Icons available in bootstack",
        description=(
            "Launch the Bootstrap Icons browser.\n\n"
            "Displays all Bootstrap Icons bundled with bootstack. "
            "Click any icon to copy its name to the clipboard — the "
            "copied name works directly as icon= on any bootstack widget."
        ),
    )
    parser.set_defaults(func=lambda args: run_icons())


# ── Layout constants ─────────────────────────────────────────────────────────
_ICON_SIZE = 28
_CELL_H = 62
_MIN_CELL_W = 88   # minimum cell width — drives column count calculation
_RENDER_BATCH = 200


def run_icons() -> None:
    import tkinter as tk
    from bootstack.signals import Signal
    from bootstack._core.images import _ImageService
    from bootstack._runtime.app import App as _App
    from bootstack.widgets._impl.primitives.frame import Frame as _Frame
    from bootstack.widgets._impl.primitives.label import Label as _Label
    from bootstack.widgets._impl.primitives.packframe import PackFrame as _PackFrame
    from bootstack.widgets._impl.primitives.scrollbar import Scrollbar as _Scrollbar
    from bootstack.widgets._impl.primitives.separator import Separator as _Separator
    from bootstack.widgets._impl.composites.textentry import TextEntry as _TextEntry

    app = _App(title="Bootstrap Icons", size=(990, 720))

    # ── Top bar ──────────────────────────────────────────────────────────────
    topbar = _PackFrame(app, direction="row", padding=(12, 8), gap=10)
    topbar.pack(fill="x")

    search = _TextEntry(topbar, width=30)
    search.insert_addon(_Label, position="before", icon="search", icon_only=True)
    search.pack(side="left")

    count_sig = Signal("loading…")
    _Label(topbar, textsignal=count_sig, font="caption", accent="muted").pack(side="right")

    _Separator(app, orient="horizontal").pack(fill="x")

    # ── Canvas + scrollbar ───────────────────────────────────────────────────
    content = _Frame(app)
    content.pack(fill="both", expand=True)

    vsb = _Scrollbar(content, orient="vertical")
    vsb.pack(side="right", fill="y")

    canvas = tk.Canvas(content, highlightthickness=0, bd=0)
    canvas.pack(side="left", fill="both", expand=True)

    canvas.configure(yscrollcommand=vsb.set)
    vsb.configure(command=canvas.yview)

    # ── Status bar ───────────────────────────────────────────────────────────
    _Separator(app, orient="horizontal").pack(fill="x")
    status_sig = Signal(
        "Click an icon to copy its name  ·  use as  icon=\"name\"  on any widget"
    )
    statusbar = _PackFrame(app, direction="row", padding=(12, 4))
    statusbar.pack(fill="x")
    _Label(statusbar, textsignal=status_sig, font="caption", accent="muted").pack(side="left")

    # ── Data + render state ──────────────────────────────────────────────────
    _, glyphmap = _ImageService._load_icon_assets()
    all_names: list[str] = sorted(glyphmap.keys())

    _photos: list[Any] = []            # strong refs — prevents Tk GC
    _item_names: dict[int, str] = {}   # canvas item id → icon name
    _current_query: list[str] = [""]
    _current_matches: list[list[str]] = [[]]
    _current_cols: list[int] = [8]
    _current_cell_w: list[int] = [_MIN_CELL_W]
    _render_gen: list[int] = [0]       # incremented on each rebuild to cancel stale batches
    _search_after: list[Any] = [None]
    _resize_after: list[Any] = [None]
    _hover_item: list[int] = [0]       # canvas item id for the hover highlight rect
    _hover_after: list[Any] = [None]   # pending after() id for click-flash restore

    def _theme_colors() -> tuple[str, str]:
        try:
            from bootstack.style.style import get_style
            style = get_style()
            return style.colors.get("background", "#ffffff"), style.colors.get("foreground", "#212529")
        except Exception:
            return "#ffffff", "#212529"

    def _blend(bg_hex: str, fg_hex: str, ratio: float) -> str:
        """Blend fg onto bg at ratio (0.0 = all bg, 1.0 = all fg)."""
        h1 = bg_hex.lstrip("#")
        h2 = fg_hex.lstrip("#")
        br, bg_c, bb = int(h1[0:2], 16), int(h1[2:4], 16), int(h1[4:6], 16)
        fr, fg_c, fb = int(h2[0:2], 16), int(h2[2:4], 16), int(h2[4:6], 16)
        r = int(br + (fr - br) * ratio)
        g = int(bg_c + (fg_c - bg_c) * ratio)
        b = int(bb + (fb - bb) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _layout() -> tuple[int, int]:
        """Return (cols, cell_w) so the grid exactly fills the canvas width."""
        w = canvas.winfo_width()
        if w <= _MIN_CELL_W:
            return 8, _MIN_CELL_W  # canvas not yet laid out
        cols = max(1, w // _MIN_CELL_W)
        cell_w = w // cols          # spread columns evenly across full width
        return cols, cell_w

    def _cell_at(cx: float, cy: float) -> int | None:
        """Return index into current matches for scroll-aware canvas coords, or None."""
        cols = _current_cols[0]
        cell_w = _current_cell_w[0]
        matches = _current_matches[0]
        if cols == 0 or cell_w == 0 or not matches:
            return None
        col = int(cx // cell_w)
        row = int(cy // _CELL_H)
        if col < 0 or col >= cols:
            return None
        idx = row * cols + col
        if idx < 0 or idx >= len(matches):
            return None
        return idx

    def _hover_rect_coords(idx: int) -> tuple[int, int, int, int]:
        cols = _current_cols[0]
        cell_w = _current_cell_w[0]
        col = idx % cols
        row = idx // cols
        return (
            col * cell_w + 2, row * _CELL_H + 2,
            (col + 1) * cell_w - 2, (row + 1) * _CELL_H - 2,
        )

    # ── Batched renderer ─────────────────────────────────────────────────────

    def _render_batch(matches: list[str], start: int, cols: int, cell_w: int,
                      fg: str, gen: int) -> None:
        if gen != _render_gen[0]:
            return  # superseded by a newer rebuild

        end = min(start + _RENDER_BATCH, len(matches))
        for i in range(start, end):
            name = matches[i]
            col = i % cols
            row = i // cols
            cx = col * cell_w + cell_w // 2
            cy = row * _CELL_H + 6

            photo = _ImageService.get_icon(name, _ICON_SIZE, fg)
            _photos.append(photo)

            img_id = canvas.create_image(
                cx, cy + _ICON_SIZE // 2, image=photo, anchor="center")
            _item_names[img_id] = name

            label = name if len(name) <= 13 else name[:11] + "…"
            txt_id = canvas.create_text(
                cx, cy + _ICON_SIZE + 5, text=label,
                anchor="n", fill=fg,
                font=("TkDefaultFont", 8),
                width=cell_w - 6)
            _item_names[txt_id] = name

            # full-cell transparent hit box (top of z-order — catches mouse events)
            box_id = canvas.create_rectangle(
                col * cell_w + 1, row * _CELL_H + 1,
                (col + 1) * cell_w - 1, (row + 1) * _CELL_H - 1,
                fill="", outline="")
            _item_names[box_id] = name

        total_rows = (len(matches) + cols - 1) // cols
        canvas.configure(
            scrollregion=(0, 0, cols * cell_w, total_rows * _CELL_H + 16))

        if end < len(matches):
            canvas.after(0, lambda: _render_batch(matches, end, cols, cell_w, fg, gen))

    def rebuild(query: str = "") -> None:
        query = query or ""
        _current_query[0] = query
        _render_gen[0] += 1
        gen = _render_gen[0]

        canvas.delete("all")
        _photos.clear()
        _item_names.clear()
        canvas.yview_moveto(0)

        q = query.strip().lower()
        matches = [n for n in all_names if q in n] if q else all_names
        count_sig.set(f"{len(matches):,} of {len(all_names):,} icons")

        bg, fg = _theme_colors()
        canvas.configure(bg=bg)

        if not matches:
            canvas.create_text(
                max(canvas.winfo_width() // 2, 160), 100,
                text=f'No icons match "{query}"',
                fill=fg, font=("TkDefaultFont", 11), anchor="center")
            _current_matches[0] = []
            _hover_item[0] = 0
            return

        cols, cell_w = _layout()
        _current_matches[0] = matches
        _current_cols[0] = cols
        _current_cell_w[0] = cell_w

        # Create hover rect FIRST so icons render on top of it
        _hover_item[0] = canvas.create_rectangle(
            0, 0, 0, 0, fill="", outline="", tags="hover")

        _render_batch(matches, 0, cols, cell_w, fg, gen)

    # ── Hover + cursor ───────────────────────────────────────────────────────

    def _on_motion(event: Any) -> None:
        if not _hover_item[0]:
            return
        cx = canvas.canvasx(event.x)
        cy = canvas.canvasy(event.y)
        idx = _cell_at(cx, cy)
        if idx is None:
            canvas.itemconfigure(_hover_item[0], fill="", outline="")
            canvas.configure(cursor="")
            return
        x1, y1, x2, y2 = _hover_rect_coords(idx)
        canvas.coords(_hover_item[0], x1, y1, x2, y2)
        bg, fg = _theme_colors()
        canvas.itemconfigure(_hover_item[0], fill=_blend(bg, fg, 0.08), outline="")
        canvas.configure(cursor="hand2")

    def _on_leave(event: Any) -> None:
        if _hover_item[0]:
            canvas.itemconfigure(_hover_item[0], fill="", outline="")
        canvas.configure(cursor="")

    canvas.bind("<Motion>", _on_motion)
    canvas.bind("<Leave>", _on_leave)

    # ── Click — copy name + press flash ─────────────────────────────────────

    def _on_click(event: Any) -> None:
        cx = canvas.canvasx(event.x)
        cy = canvas.canvasy(event.y)
        idx = _cell_at(cx, cy)
        if idx is None:
            return
        name = _current_matches[0][idx]

        # Press flash: darken highlight for 150 ms then restore to hover tint
        if _hover_item[0]:
            bg, fg = _theme_colors()
            canvas.itemconfigure(_hover_item[0], fill=_blend(bg, fg, 0.22))
            if _hover_after[0] is not None:
                app.after_cancel(_hover_after[0])

            def _restore_hover() -> None:
                if _hover_item[0]:
                    b, f = _theme_colors()
                    canvas.itemconfigure(_hover_item[0], fill=_blend(b, f, 0.08))
                _hover_after[0] = None

            _hover_after[0] = app.after(150, _restore_hover)

        app.clipboard_clear()
        app.clipboard_append(name)
        status_sig.set(
            f"Copied  \"{name}\"  —  ready to paste as  icon=\"{name}\"")
        app.after(3000, lambda: status_sig.set(
            "Click an icon to copy its name  ·  use as  icon=\"name\"  on any widget"))

    canvas.bind("<Button-1>", _on_click)

    # ── Scrolling ────────────────────────────────────────────────────────────

    canvas.bind("<MouseWheel>",
                lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    # ── Search (debounced 120 ms) ─────────────────────────────────────────────

    def _on_search(event: Any) -> None:
        query = (getattr(event.data, "value", "") or "") if hasattr(event, "data") else ""
        if _search_after[0] is not None:
            app.after_cancel(_search_after[0])
        _search_after[0] = app.after(120, lambda: rebuild(query))

    search.on_changed(_on_search)

    # ── Resize (debounced 80 ms) ──────────────────────────────────────────────

    def _on_resize(event: Any) -> None:
        if _resize_after[0] is not None:
            app.after_cancel(_resize_after[0])
        _resize_after[0] = app.after(80, lambda: rebuild(_current_query[0]))

    canvas.bind("<Configure>", _on_resize)

    # ── Theme change ──────────────────────────────────────────────────────────

    app.bind("<<ThemeChanged>>",
             lambda e: rebuild(_current_query[0]), add="+")

    # ── First paint ───────────────────────────────────────────────────────────

    app.after(60, lambda: rebuild(""))

    app.mainloop()
    sys.exit(0)