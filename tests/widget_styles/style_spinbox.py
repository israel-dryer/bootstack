import bootstack as bs
from bootstack.constants import *


def create_spinbox_test():
    frame = bs.Frame(padding=10)

    # title
    title = bs.Label(frame, text='Spinbox', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    spinbox = bs.Spinbox(frame)
    spinbox.pack(padx=5, pady=5, fill=BOTH)
    spinbox.insert(END, 'default')

    # color
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        spinbox = bs.Spinbox(frame, accent=color)
        spinbox.pack(padx=5, pady=5, fill=BOTH)
        spinbox.insert(END, color)

    # disabled
    spinbox = bs.Spinbox(frame)
    spinbox.insert(END, 'disabled')
    spinbox.configure(state=DISABLED)
    spinbox.pack(padx=5, pady=5, fill=BOTH)

    # readonly
    spinbox = bs.Spinbox(frame)
    spinbox.insert(END, 'readonly')
    spinbox.configure(state='readonly')
    spinbox.pack(padx=5, pady=5, fill=BOTH)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    test1 = create_spinbox_test()
    test1.pack(side=LEFT, fill=BOTH)

    root.mainloop()
