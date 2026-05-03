import bootstack as bs
from bootstack.constants import *


def create_notebook_frame(bootstyle, test_name):
    frame = bs.Frame(root, padding=5)

    # title
    title = bs.Label(frame, text=test_name, anchor=CENTER)
    title.pack(padx=5, pady=2, fill=BOTH)
    colors = ['primary', 'secondary', 'success', 'info', 'warning', 'danger']

    # default
    nb = bs.Notebook(frame, height=50, width=100, variant=bootstyle)
    nb.pack(padx=5, pady=5, fill=BOTH)
    for i, _ in enumerate(colors):
        if i % 2 == 0:
            nb.add(bs.Frame(nb), text=f'Tab {i + 1}')

    # other colors
    for color in colors:
        nb = bs.Notebook(frame, accent=color, variant=bootstyle, height=50, width=100)
        nb.pack(padx=5, pady=5, fill=BOTH)
        for i, _ in enumerate(colors):
            nb.add(bs.Frame(nb), text=f'Tab {i + 1}')
    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_notebook_frame('default', 'Tabs').pack(side=LEFT)
    create_notebook_frame('pill', 'Pills').pack(side=LEFT)
    create_notebook_frame('bar', 'Bars').pack(side=LEFT)

    root.mainloop()
