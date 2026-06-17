"""Icons command — launches the Bootstrap Icons browser."""
from __future__ import annotations

import argparse


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


_DEFAULT_STATUS = (
    'Click an icon to copy its name  ·  use as  icon="name"  on any widget'
)


def run_icons() -> None:
    import bootstack as bs
    from bootstack.clipboard import set_clipboard
    from bootstack.data import MemoryDataSource, col
    from bootstack.images import get_icon, list_icons

    names = list_icons()

    with bs.App(title="Bootstrap Icons", size=(990, 720), gap=0) as app:
        # Each record carries a theme-following Image. Gallery recycles its tiles,
        # so the thumbnails render lazily as they scroll into view and recolor
        # with the theme on their own — no manual batching or repaint needed.
        records = [
            {"id": i, "name": name, "icon": get_icon(name, size=32)}
            for i, name in enumerate(names)
        ]
        source = MemoryDataSource()
        source.load(records)

        count = bs.Signal("")
        status = bs.Signal(_DEFAULT_STATUS)

        def update_count() -> None:
            count.set(f"{source.count:,} of {len(names):,} icons")

        with bs.Row(padding=(12, 8), gap=10, horizontal="stretch", vertical_items="center"):
            search = bs.TextField(placeholder="Search icons", grow=True)
            search.insert_addon("label", "before", icon="search")
            bs.Label(textsignal=count, font="caption", accent="muted")

        bs.Divider()

        gallery = bs.Gallery(
            data_source=source,
            image_field="icon",
            caption_field="name",
            columns="auto",
            tile_size=(72, 40),
            fit="none",            # show the 32px glyph at native size — crisp, no upscale
            gap=6,
            selection_mode="single",
            grow=True,
            horizontal="stretch",
        )

        bs.Divider()

        with bs.Row(padding=(12, 4), horizontal="stretch", surface="chrome"):
            bs.Label(textsignal=status, font="caption", accent="muted")

        def on_search(event) -> None:
            query = event.text.strip().lower()
            source.where(col("name").contains(query) if query else None)
            gallery.reload()
            update_count()

        # Live, as-you-type filtering — debounced so a fast typist isn't reloaded
        # on every keystroke.
        search.on_input().debounce(120).listen(on_search)

        def on_pick(record: dict) -> None:
            name = record["name"]
            set_clipboard(name)
            status.set(f'Copied  "{name}"  —  ready to paste as  icon="{name}"')

        gallery.on_item_click(on_pick)

        update_count()

    app.run()

if __name__ == '__main__':
    run_icons()