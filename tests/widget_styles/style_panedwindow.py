import bootstack as bs
from bootstack.constants import *


def create_panedwindow_frame():
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text='Paned Window', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    pw = bs.PanedWindow(frame)
    pw.pack(padx=5, pady=5, fill=BOTH)
    pw.add(bs.Frame(pw, width=100, height=50, accent='info'))
    pw.add(bs.Frame(pw, width=100, height=50, accent='success'))

    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        pw = bs.PanedWindow(frame, accent=color)
        pw.pack(padx=5, pady=5, fill=BOTH)
        pw.add(bs.Frame(pw, width=100, height=50))
        pw.add(bs.Frame(pw, width=100, height=50))

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)
    create_panedwindow_frame().pack(side=LEFT)

    root.mainloop()
