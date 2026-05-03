import bootstack as bs
from bootstack.constants import *


def create_checkbutton_test(name):
    frame = bs.Frame(padding=10)

    # title
    title = bs.Label(frame, text=name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default style
    cb = bs.Switch(frame, text='default')
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    # color styles
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        cb = bs.Switch(
            master=frame,
            text=color,
            accent=color,
            width=15
        )
        cb.pack(padx=5, pady=5, fill=BOTH)
        cb.invoke()

    # disabled style
    cb = bs.Switch(
        master=frame,
        text='disabled',
        state=DISABLED
    )
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    app = bs.App("CheckButton Demo")

    test3 = create_checkbutton_test( 'Switch')
    test3.pack(side='left', fill=BOTH)

    btn = bs.Button(text="Change Theme", command=bs.toggle_theme)
    btn.pack(padx=10, pady=10)

    app.mainloop()
