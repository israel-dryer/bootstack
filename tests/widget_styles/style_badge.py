import bootstack as bs
from bootstack.constants import *


def create_badge_style(variant, test_name):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=test_name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    # default
    badge = bs.Badge(frame, text='default', variant=variant)
    badge.pack(padx=5, pady=5)

    # colored
    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        lbl = bs.Badge(frame, text=color, accent=color, variant=variant, anchor='center')
        lbl.pack(padx=5, pady=5)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()
    style = bs.Style()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_badge_style('square', 'Square').pack(side=LEFT)
    create_badge_style('pill', 'Pill').pack(side=LEFT)

    root.mainloop()
