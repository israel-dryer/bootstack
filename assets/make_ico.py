from pathlib import Path
from PIL import Image

assets = Path(__file__).parent
dest = Path(__file__).parent.parent / "src" / "bootstack" / "assets"
sizes = [16, 24, 32, 48, 64, 128, 256]


def make_ico(src_dir: Path, out_path: Path) -> None:
    imgs = [Image.open(src_dir / f"icon-{s}.png").convert("RGBA") for s in sizes]
    # Pass largest first — Pillow skips sizes larger than the base image
    imgs[-1].save(
        out_path,
        format="ICO",
        bitmap_format="bmp",  # BMP encoding for maximum Windows compatibility
        sizes=[(s, s) for s in sizes],
        append_images=imgs[:-1],
    )
    print(f"Saved: {out_path}")


make_ico(assets / "light", dest / "bootstack-light.ico")
make_ico(assets / "dark", dest / "bootstack-dark.ico")