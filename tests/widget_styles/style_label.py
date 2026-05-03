import bootstack as bs
from bootstack.constants import *


def create_label_style(test_name):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=test_name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    lbl = bs.Label(frame, text='default')
    lbl.pack(padx=5, pady=5, fill=X)

    # colored
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        lbl = bs.Label(frame, text=color, accent=color)
        lbl.pack(padx=5, pady=5, fill=X)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_label_style('Label').pack(side=LEFT, fill=X)

    root.mainloop()
