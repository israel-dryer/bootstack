import bootstack as bs
from bootstack.constants import *


def create_labelframe_style():
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text='Labelframe', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    lbl = bs.LabelFrame(
        master=frame,
        text='default',
        width=150,
        height=75
    )
    lbl.pack(padx=5, pady=5, fill=BOTH)

    # colored
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        lbl = bs.LabelFrame(
            master=frame,
            text=color,
            accent=color,
            width=150,
            height=75
        )
        lbl.pack(padx=5, pady=5, fill=BOTH)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_labelframe_style().pack(side=LEFT)

    root.mainloop()
