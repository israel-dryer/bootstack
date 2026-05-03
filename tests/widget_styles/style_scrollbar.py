import bootstack as bs
from bootstack.constants import *


def create_scrollbar_frame(orient, bootstyle=''):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=bootstyle.title() + ' Scrollbar', anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    bs.Label(frame, text='default').pack(fill=X)
    sb = bs.Scrollbar(frame, orient=orient, variant=bootstyle)
    sb.set(0.1, 0.9)
    if orient == HORIZONTAL:
        sb.pack(padx=5, pady=5, fill=X)
    else:
        sb.pack(padx=5, pady=5, fill=Y, side=LEFT)

    # colored
    for _, color in enumerate(['primary', 'secondary', 'success', 'info', 'warning', 'danger']):
        bs.Label(frame, text=color).pack(fill=X)
        sb = bs.Scrollbar(frame, accent=color, variant=bootstyle, orient=orient)
        sb.set(0.1, 0.3)
        if orient == HORIZONTAL:
            sb.pack(padx=5, pady=5, fill=X, expand=YES)
        else:
            sb.pack(padx=5, pady=5, fill=Y, side=LEFT,
                    expand=YES)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()
    root.geometry('1000x500')
    style = bs.Style()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)
    test1 = create_scrollbar_frame(orient=HORIZONTAL, bootstyle='default')
    test1.pack(side=LEFT, anchor=N, fill=BOTH, expand=YES)

    test2 = create_scrollbar_frame(orient=VERTICAL, bootstyle='default')
    test2.pack(side=LEFT, anchor=N, fill=BOTH, expand=YES)

    test3 = create_scrollbar_frame(orient=HORIZONTAL, bootstyle='square')
    test3.pack(side=LEFT, anchor=N, fill=BOTH, expand=YES)

    test4 = create_scrollbar_frame(orient=VERTICAL, bootstyle='square')
    test4.pack(side=LEFT, anchor=N, fill=BOTH, expand=YES)

    root.mainloop()
