import bootstack as bs
from bootstack.constants import *


def create_scale_frame(orient):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=orient.title() + ' Scale', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    pb = bs.Scale(
        master=frame,
        orient=orient,
        value=0.2
    )
    if orient == HORIZONTAL:
        pb.pack(padx=5, pady=5, fill=BOTH)
    else:
        pb.pack(padx=5, pady=5, fill=BOTH, side=LEFT)

    # colored
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        bs.Label(frame, text=color).pack(fill=X)
        pb = bs.Scale(
            master=frame,
            value=0.2,
            accent=color,
            orient=orient
        )
        if orient == HORIZONTAL:
            pb.pack(padx=5, pady=5, fill=BOTH)
        else:
            pb.pack(padx=5, pady=5, fill=BOTH, side=LEFT)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    test1 = create_scale_frame(HORIZONTAL)
    test1.pack(side=LEFT, anchor=N)
    test2 = create_scale_frame(VERTICAL)
    test2.pack(side=LEFT, anchor=N)

    root.mainloop()
