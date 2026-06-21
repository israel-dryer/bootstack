"""README "Widget Gallery" screenshot, captured from the live demo.

Builds the same shell as ``bootstack demo`` (via the shared
``build_gallery_shell``) and lands on the Data Tables page, so the README
gallery shot always matches the live demo — no manual capture.

Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py demo

The demo carries a lot of widgets, so the dark capture (a theme switch) can take
a moment. Copy the result into assets/readme/ for the README::

    copy docs\\_static\\examples\\demo-gallery-light.png assets\\readme\\gallery-light.png
    copy docs\\_static\\examples\\demo-gallery-dark.png  assets\\readme\\gallery-dark.png
"""
import bootstack as bs
from bootstack.cli.demo import build_gallery_shell


def gallery():
    with bs.AppShell(title="Widget Gallery", size=(1100, 750)) as shell:
        shell._capture_full_window = True
        build_gallery_shell(shell)
        shell.navigate("tables")
    shell.run()


SCENES = {
    "gallery": gallery,
}
