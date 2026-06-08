import bootstack as bs

from bootstack.dialogs import ColorChooserDialog
def show_chooser():
    result = bs.ask_color(title="Choose Color", color="#0070C0")
    if result:
        print(f"Selected: hex={result.hex}  rgb={result.rgb}  hsl={result.hsl}")

def show_custom():
    dlg = ColorChooserDialog(title="Background Color", color="#00B050")
    dlg.show()
    if dlg.result:
        print(f"hex={dlg.result.hex}")

with bs.App(title="Color Dialog", size=(680, 160), padding=20, gap=16) as app:

    bs.Label("Color Dialog", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("ask_color()",          on_click=show_chooser)
        bs.Button("ColorChooserDialog()", on_click=show_custom)

app.run()