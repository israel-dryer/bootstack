import bootstack as bs
from bootstack.constants import *


def create_radiobutton_test(bootstyle, testname):
    frame = bs.Frame(padding=10)

    var = bs.Variable()

    # title
    title = bs.Label(frame, text=testname, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default style
    cb = bs.RadioButton(frame, text='default', variant=bootstyle, value=0)
    cb.configure(variable=var)
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    # color styles
    for i, color in enumerate(['primary', 'secondary', 'success', 'info', 'warning', 'danger']):
        cb = bs.RadioButton(frame, text=color, accent=color, variant=bootstyle)
        cb.configure(variable=var, value=i + 1)
        cb.pack(padx=5, pady=5, fill=BOTH)
        cb.invoke()

    # disabled style
    cb = bs.RadioButton(
        master=frame,
        text='disabled',
        variant=bootstyle,
        state=DISABLED,
        variable=var,
        value=i + 1
    )
    cb.pack(padx=5, pady=5, fill=BOTH)
    cb.invoke()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    test1 = create_radiobutton_test('default', 'Radiobutton')
    test1.pack(side=LEFT, fill=BOTH)

    root.mainloop()
