"""App icon command — a visual designer for application icons.

Launches a small bootstack app that previews an `AppIcon` live as you adjust the
glyph, colors, and corner radius, then exports it (`.ico`/`.icns`/`.png`) or
copies a ready-to-paste ``[build.icon]`` snippet for ``bootstack.toml``.
"""
from __future__ import annotations

import argparse

from bootstack.widgets.types import IconSpec
from bootstack.clipboard import set_clipboard


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "appicon",
        help="Design an application icon and export it",
        description=(
            "Launch the app icon designer.\n\n"
            "Pick a Bootstrap glyph, choose background and foreground colors and "
            "a corner radius, and preview the result live at several sizes. Export "
            "an .ico / .icns / .png for a packaged build, or copy a [build.icon] "
            "snippet for bootstack.toml. (Find glyph names with `bootstack icons`.)"
        ),
    )
    parser.set_defaults(func=lambda args: run_appicon())


# Windows/Linux preview sizes (glyph-only), largest first.
_PREVIEW_SIZES = [96, 64, 48, 32, 16]
# macOS preview size (the rounded tile).
_MACOS_SIZE = 196

_HEX_DIGITS = set("0123456789abcdefABCDEF")


def _is_hex(color: str) -> bool:
    return (
        color.startswith("#")
        and len(color) in (4, 7, 9)
        and all(ch in _HEX_DIGITS for ch in color[1:])
    )


def run_appicon() -> None:
    import bootstack as bs
    from bootstack.images import AppIcon, list_icons

    state: dict = {"jobs": {}, "win_imgs": [], "mac_img": None}

    with bs.App(title="App Icon Designer", size=(800, 600)) as app:
        # Signals require the application root, so create them inside the context.
        glyph_sig = bs.Signal("rocket")
        bg_sig = bs.Signal("#0d6efd")
        fg_sig = bs.Signal("#ffffff")
        radius_sig = bs.Signal(0.22)
        dark_sig = bs.Signal(False)
        status_sig = bs.Signal("Adjust settings to see live preview")

        with bs.HStack(fill='both', anchor="n", expand=True):

            # ── Controls ──────────────────────────────────────────────────────
            with bs.VStack(padding=16, gap=24, anchor_items="n", anchor="n", fill="y"):
                bs.Label("App Icon Designer", font="heading-md")
                bs.Label(textsignal=status_sig, font="caption", accent="muted", wrap_width=225)

                gl = bs.TextField(textsignal=glyph_sig, fill="x", label="Glyph")
                gl.insert_addon("button", "after", icon="grid-fill", on_click=lambda: _open_picker(gl))

                bg = bs.TextField(textsignal=bg_sig, fill="x", label="Background color")
                bg.insert_addon("button", "after", icon="palette-fill", on_click=lambda: _pick(bg_sig))

                fg = bs.TextField(textsignal=fg_sig, fill="x", label="Foreground")
                fg.insert_addon("button", "after", icon="palette-fill", on_click=lambda: _pick(fg_sig))

                bs.NumberField(signal=radius_sig, min_value=0.00, max_value=0.50, step=0.01, fill='x', label="Corner radius (macOS tile)")

                with bs.HStack(fill='x'):
                    bs.Label("Preview Dark Theme", fill='x', expand=True)
                    bs.Switch(None, signal=dark_sig, anchor="w")

                with bs.HStack(gap=6, fill="both", fill_items='x', expand_items=True, expand=True, anchor_items="s"):
                    bs.Button("Export…", accent="primary", on_click=lambda: _export())
                    bs.Button("Copy TOML", variant="outline", on_click=lambda: _copy_toml())


            bs.Separator(orient="vertical", fill="y")

            # ── Preview ───────────────────────────────────────────────────────
            with bs.VStack(padding=16, fill="both", expand=True, anchor_items="center"):
                preview = bs.Grid(rows=2, columns=1, gap=10, fill="both", expand=True)


    def _current_icon() -> "AppIcon":
        # shape="auto" — exports glyph-only for .ico/.png, a tile for .icns.
        return AppIcon(
            glyph_sig() or "rocket",
            background=bg_sig(),
            foreground=fg_sig(),
            radius=radius_sig(),
        )

    def _colors_ok() -> bool:
        return _is_hex(bg_sig()) and _is_hex(fg_sig())

    def _win_tiled(icon: "AppIcon", size: int) -> bool:
        # Mirror the real shape='auto' .ico: glyph-only at small title-bar frames,
        # a tile at taskbar sizes and up — so the preview matches the export.
        return icon._tiled_for_size(size, suffix=".ico")

    def _build_preview() -> None:
        # Build the preview skeleton ONCE; updates swap images in place so the
        # screen never flashes from tearing down and rebuilding the widgets.
        icon = _current_icon()
        win_imgs: list = []

        with bs.VStack(parent=preview, row=0, column=0, gap=4, anchor_items="center"):
            bs.Label("Windows / Linux", font="caption", accent="muted")
            with bs.HStack(gap=12, anchor_items="s"):
                for size in _PREVIEW_SIZES:
                    tiled = _win_tiled(icon, size)
                    with bs.VStack(gap=2):
                        img = bs.Label(image=icon.to_image(size, tiled=tiled))
                        bs.Label(f"{size}px", font="caption", accent="muted", anchor="s")
                        win_imgs.append((size, tiled, img))

        with bs.VStack(parent=preview, row=1, column=0, gap=4, anchor_items="center"):
            bs.Label("macOS", font="caption", accent="muted")
            mac_img = bs.Label(image=icon.to_image(_MACOS_SIZE, tiled=True))

        state["win_imgs"] = win_imgs
        state["mac_img"] = mac_img

    def _colors_ready() -> bool:
        if not _colors_ok():
            status_sig.set("Colors must be hex values (e.g. #0d6efd).")
            return False
        status_sig.set("Adjust the settings — the preview updates live.")
        return True

    def _update_tiles() -> None:
        # Foreground and corner radius only affect TILED frames — the macOS tile
        # and the larger Windows/Linux frames. The small glyph-only frames are
        # unchanged, so they are left in place.
        if state.get("rendering") or not _colors_ready():
            return
        state["rendering"] = True
        try:
            icon = _current_icon()
            for size, tiled, img in state["win_imgs"]:
                if tiled:
                    img.image = icon.to_image(size, tiled=True)
            state["mac_img"].image = icon.to_image(_MACOS_SIZE, tiled=True)
        finally:
            state["rendering"] = False

    def _update_all() -> None:
        # Guard against re-entrancy: a scheduled update can fire inside a modal
        # dialog's nested event loop (e.g. while the color picker is open), which
        # could otherwise overlap an in-progress swap.
        if state.get("rendering") or not _colors_ready():
            return
        state["rendering"] = True
        try:
            icon = _current_icon()
            # Swap each image in place — no widget rebuild, no flicker. Each frame
            # keeps the shape it was built with (small = glyph-only, large = tile).
            for size, tiled, img in state["win_imgs"]:
                img.image = icon.to_image(size, tiled=tiled)
            state["mac_img"].image = icon.to_image(_MACOS_SIZE, tiled=True)
        finally:
            state["rendering"] = False

    def _schedule(key: str, fn) -> None:
        # Coalesce rapid signal changes (e.g. dragging the radius slider) into
        # one update via the framework scheduler (cancelable Job, lifetime-tied).
        job = state["jobs"].get(key)
        if job is not None:
            job.cancel()
        state["jobs"][key] = app.schedule.delay(80, fn)

    def _pick(target: "bs.Signal") -> None:
        choice = bs.ask_color()
        if choice is not None:
            target.set(choice.hex)

    def _apply_theme(*_) -> None:
        app.theme = "bootstrap-dark" if dark_sig() else "bootstrap-light"

    def _open_picker(parent) -> None:
        all_names = list_icons()
        pick: dict = {"job": None, "grid": None}

        with bs.Window(title="Choose an icon", size=(500, 500), parent=parent) as win:
            query = bs.Signal("")
            count = bs.Signal("")
            with bs.VStack(padding=12, gap=8, fill="both", expand=True):
                bs.TextField(textsignal=query, placeholder="Search icons…", fill="x")
                bs.Label(textsignal=count, font="caption", accent="muted")
                scroller = bs.ScrollView(fill="both", expand=True, height=430)

        def _choose(name: str) -> None:
            glyph_sig.set(name)
            win.close()

        def _rebuild_grid(*_) -> None:
            if pick["grid"] is not None:
                pick["grid"].destroy()
            q = (query() or "").strip().lower()
            matches = [n for n in all_names if q in n] if q else all_names
            shown = matches[:120]
            count.set(
                f"{len(matches):,} icons"
                + (" — showing first 120, refine to narrow" if len(matches) > 120 else "")
            )
            with bs.Grid(parent=scroller, columns=8, gap=2) as grid:
                for name in shown:
                    spec: IconSpec = {"name": name, "size": 36}
                    bs.Button(
                        icon=spec,
                        icon_only=True,
                        variant="ghost",
                        on_click=lambda n=name: _choose(n),
                    )
            pick["grid"] = grid

        def _on_query(*_) -> None:
            # Debounce search via the window's own scheduler (auto-cancels when
            # the picker closes).
            if pick["job"] is not None:
                pick["job"].cancel()
            pick["job"] = win.schedule.delay(150, _rebuild_grid)

        query.subscribe(_on_query)
        _rebuild_grid()
        # Open beside the trigger — the window's top-left at the field's top-right.
        win.show(anchor_to=parent, anchor_point="ne", window_point="nw", offset=(8, 0))

    def _export() -> None:
        if not _colors_ok():
            status_sig.set("Fix the colors before exporting.")
            return
        path = bs.ask_save_file(
            title="Export app icon",
            default_extension=".ico",
            initial_file=f"{glyph_sig() or 'app'}.ico",
            file_types=[
                ("Windows icon", "*.ico"),
                ("macOS icon", "*.icns"),
                ("PNG image", "*.png"),
            ],
        )
        if not path:
            return
        try:
            _current_icon().save(path)
            status_sig.set(f"Exported to {path}")
        except Exception as exc:  # pragma: no cover - surfaced to the user
            status_sig.set(f"Could not export: {exc}")

    def _copy_toml() -> None:
        snippet = (
            "[build.icon]\n"
            f'glyph = "{glyph_sig() or "rocket"}"\n'
            f'background = "{bg_sig()}"\n'
            f'foreground = "{fg_sig()}"\n'
            f"radius = {round(radius_sig(), 3)}\n"
        )
        set_clipboard(snippet)
        status_sig.set("Copied [build.icon] snippet to the clipboard.")

    _build_preview()
    # Glyph and background affect every frame; foreground and corner radius affect
    # only the tiled frames (the macOS tile and the larger Windows/Linux frames),
    # so those re-render just the tiles.
    glyph_sig.subscribe(lambda *_: _schedule("all", _update_all))
    bg_sig.subscribe(lambda *_: _schedule("all", _update_all))
    fg_sig.subscribe(lambda *_: _schedule("tiles", _update_tiles))
    radius_sig.subscribe(lambda *_: _schedule("tiles", _update_tiles))
    dark_sig.subscribe(_apply_theme)
    app.run()

if __name__ == '__main__':
    run_appicon()