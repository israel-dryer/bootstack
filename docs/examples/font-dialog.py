import bootstack as bs

def show_font():
    font = bs.ask_font(title="Select Font")
    if font:
        print(f"Selected: {font.actual()}")

def show_fixed():
    dlg = bs.FontDialog(title="Code Font", default_font="TkFixedFont")
    dlg.show()
    if dlg.result:
        print(f"font={dlg.result.actual()}")

with bs.App(title="Font Dialog", size=(1000, 800), padding=20, gap=16) as app:

    bs.Label("Font Dialog", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("ask_font()",  on_click=show_font)
        bs.Button("FontDialog()", on_click=show_fixed)

app.run()