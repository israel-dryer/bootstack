import bootstack as bs
from bootstack.constants import *
from bootstack.style.style import get_style


def create_entry_test():
    frame = bs.Frame(padding=10)

    # title
    title = bs.Label(frame, text='Entry', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    entry = bs.DateEntry(frame)
    entry.pack(padx=5, pady=5, fill=BOTH)
    entry.insert(END, 'default')

    # color
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        entry = bs.DateEntry(frame, bootstyle=color)
        entry.pack(padx=5, pady=5, fill=BOTH)
        entry.insert(END, color)

    # readonly
    entry = bs.DateEntry(frame)
    entry.insert(END, 'readonly')
    entry.configure(state=READONLY)
    entry.pack(padx=5, pady=5, fill=BOTH)

    # disabled
    entry = bs.DateEntry(frame)
    entry.insert(END, 'disabled')
    entry.configure(state=DISABLED)
    entry.pack(padx=5, pady=5, fill=BOTH)

    return frame


def change_style():
    if style.theme_use() == 'dark':
        style.theme_use('light')
    else:
        style.theme_use('dark')


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()
    style = get_style()

    bs.Button(text="Change Theme", command=change_style).pack(padx=10, pady=10)

    test1 = create_entry_test()
    test1.pack(side=LEFT, fill=BOTH)

    root.mainloop()
