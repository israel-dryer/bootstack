import bootstack as bs
from bootstack.constants import *


def create_menubutton_frame(bootstyle, testname):
    frame = bs.Frame(root, padding=5)

    title = bs.Label(
        master=frame,
        text=testname,
        anchor=CENTER
    )
    title.pack(padx=5, pady=2, fill=BOTH)

    bs.Separator(frame).pack(padx=5, pady=5, fill=X)

    btn = bs.MenuButton(
        master=frame,
        variant=bootstyle,
        text='default',
    )
    btn.pack(padx=5, pady=5, fill=BOTH)

    btn = bs.MenuButton(
        master=frame,
        variant=bootstyle,
        density='compact',
        text='compact',
    )
    btn.pack(padx=5, pady=5, fill=BOTH)

    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger']:
        btn = bs.MenuButton(
            master=frame,
            text=color,
            accent=color,
            variant=bootstyle
        )
        btn.pack(padx=5, pady=5, fill=BOTH)

    btn = bs.MenuButton(
        master=frame,
        text='disabled',
        state=DISABLED,
        variant=bootstyle,
    )
    btn.pack(padx=5, pady=5, fill=BOTH)

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.Window()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)

    create_menubutton_frame("default", 'Solid Menubutton').pack(side=LEFT)
    create_menubutton_frame('outline', 'Outline Menubutton').pack(side=LEFT)
    create_menubutton_frame('ghost', 'Ghost Menubutton').pack(side=LEFT)
    create_menubutton_frame('text', 'Text Menubutton').pack(side=LEFT)

    root.mainloop()
