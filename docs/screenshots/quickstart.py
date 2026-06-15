"""Screenshots for the Quick Start guide.

One scene per code block — the Hello bootstack window and the AppShell navigation
window. Each captures the full OS window. Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py quickstart
"""
import bootstack as bs


def hello():
    with bs.App(title="Hello", size=(340, 250), padding=16, gap=16) as app:
        app._capture_full_window = True
        bs.Label("Hello from bootstack!")
        bs.Button("Primary", accent="primary")
        bs.Button("Success", accent="success")
        bs.Button("Danger Outline", accent="danger", variant="outline")
    app.run()


def navigation():
    with bs.AppShell(title="My App", size=(720, 460)) as shell:
        shell._capture_full_window = True
        with shell.add_page("home", text="Home", icon="house"):
            with bs.VStack(padding=20, gap=8):
                bs.Label("Welcome!", font="heading-lg")
                bs.Label("Select a page from the sidebar.", accent="secondary")
        with shell.add_page("data", text="Data", icon="table"):
            with bs.VStack(padding=20, gap=8):
                bs.Label("Your data goes here.", font="heading-lg")
        shell.navigate("home")
    shell.run()


SCENES = {
    "hello": hello,
    "navigation": navigation,
}
