import bootstack as bs
from bootstack.constants import *


def create_sizegrip_style(bootstyle):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(
        master=frame,
        text='Sizegrip',
        anchor=CENTER
    )
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    bs.Label(frame, text=bootstyle).pack(fill=X)
    sg = bs.SizeGrip(frame)
    sg.pack(padx=5, pady=5, fill=BOTH, expand=True)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_sizegrip_style('default').pack(
        side=LEFT, fill=BOTH, expand=True
    )

    root.mainloop()
