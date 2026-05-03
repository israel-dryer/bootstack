import bootstack as bs
from bootstack.constants import *

def create_radio_toggle_test(bootstyle, name):
    frame = bs.Frame(padding=10)

    # title
    title = bs.Label(frame, text=name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    sig = bs.Signal('primary')

    # default style
    cb = bs.RadioToggle(frame, text='default', variant=bootstyle)
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    # color styles
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        cb = bs.RadioToggle(
            master=frame,
            text=color,
            signal=sig,
            value=color,
            accent=color,
            variant=bootstyle,
            width=15
        )
        cb.pack(padx=5, pady=5, fill=BOTH)
        cb.invoke()

    # disabled style
    cb = bs.RadioToggle(
        master=frame,
        text='disabled',
        value='disabled',
        variant=bootstyle,
        state=DISABLED
    )
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.App(title="RadioToggle Test")

    test4 = create_radio_toggle_test('default','Default')
    test4.pack(side='left', fill=BOTH)
    test5 = create_radio_toggle_test('outline','Outline')
    test5.pack(side='left', fill=BOTH)
    test6 = create_radio_toggle_test('ghost','Ghost')
    test6.pack(side='left', fill=BOTH)

    btn = bs.Button(text="Change Theme", command=bs.toggle_theme)
    btn.pack(padx=10, pady=10)

    root.mainloop()
