import bootstack as bs

from bootstack.dialogs import FontDialog
def show_font():
    choice = bs.ask_font(title="Select Font")
    if choice:
        print(f"Selected: {choice.family} {choice.size}pt {choice.weight}")

def show_code():
    dlg = FontDialog(title="Code Font", default_font="code")
    dlg.show()
    if dlg.result:
        print(f"font={dlg.result.family} {dlg.result.size}pt {dlg.result.weight}")

with bs.App(title="Font Dialog", size=(1000, 800), padding=20, gap=16) as app:

    bs.Label("Font Dialog", font="heading-sm")
    with bs.HStack(gap=8):
        bs.Button("ask_font()",  on_click=show_font)
        bs.Button("FontDialog()", on_click=show_code)

app.run()
