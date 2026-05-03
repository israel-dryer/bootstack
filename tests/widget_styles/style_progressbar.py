import bootstack as bs
from bootstack.constants import *


def create_progressbar_frame(bootstyle, orient, testname):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=testname, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    for i, color in enumerate(['primary', 'secondary', 'success', 'info', 'warning', 'danger']):
        bs.Label(frame, text=color).pack(fill=X)
        pb = bs.Progressbar(
            master=frame,
            value=25 + ((i - 1) * 10),
            accent=color,
            variant=bootstyle,
            orient=orient
        )
        if orient == 'h':
            pb.pack(padx=5, pady=5, fill=X)
        else:
            pb.pack(padx=5, pady=5, fill=Y)
        pb.start()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    test1 = create_progressbar_frame('default', 'horizontal', 'Solid Progressbar')
    test1.pack(side=LEFT)

    test2 = create_progressbar_frame('striped', 'horizontal', 'Striped Progressbar')
    test2.pack(side=LEFT)

    test2 = create_progressbar_frame('thin', 'horizontal', 'Thin Progressbar')
    test2.pack(side=LEFT)

    test3 = create_progressbar_frame('default', 'vertical', 'Solid Progressbar')
    test3.pack(side=LEFT)

    test4 = create_progressbar_frame('striped', 'vertical', 'Striped Progressbar')
    test4.pack(side=LEFT)

    test4 = create_progressbar_frame('thin', 'vertical', 'Thin Progressbar')
    test4.pack(side=LEFT)

    root.mainloop()
