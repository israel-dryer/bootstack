import bootstack as bs
from bootstack.constants import *

def create_check_toggle_test(bootstyle, name):
    frame = bs.Frame(padding=10)

    # title
    title = bs.Label(frame, text=name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default style
    cb = bs.CheckToggle(frame, text='default', variant=bootstyle)
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    # default style
    cb = bs.CheckToggle(frame, text='Compact', icon='gear-fill', variant=bootstyle, density='compact')
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()


    # color styles
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        cb = bs.CheckToggle(
            master=frame,
            text=color,
            accent=color,
            variant=bootstyle,
            width=15
        )
        cb.pack(padx=5, pady=5, fill=BOTH)
        cb.invoke()

    # disabled style
    cb = bs.CheckToggle(
        master=frame,
        text='disabled',
        variant=bootstyle,
        state=DISABLED
    )
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.App(title="CheckToggle Test")

    test4 = create_check_toggle_test('default','Default')
    test4.pack(side='left', fill=BOTH)
    test5 = create_check_toggle_test('outline','Outline')
    test5.pack(side='left', fill=BOTH)
    test6 = create_check_toggle_test('ghost','Ghost')
    test6.pack(side='left', fill=BOTH)

    btn = bs.Button(text="Change Theme", command=bs.toggle_theme)
    btn.pack(padx=10, pady=10)

    root.mainloop()
