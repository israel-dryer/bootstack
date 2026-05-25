import bootstack as bs


def create_menubutton_frame(master, variant, testname):

    frame = bs.PackFrame(master, padding=16, gap=8, fill_items='both')

    bs.Label(master=frame, text=testname, anchor='center').pack()
    bs.Separator(frame).pack()
    bs.MenuButton(master=frame, variant=variant, text='default').pack()
    bs.MenuButton(master=frame, variant=variant, density='compact', text='compact').pack()

    for color in ['primary', 'success', 'warning', 'danger']:
        bs.MenuButton(master=frame, text=color, accent=color, variant=variant).pack()

    bs.MenuButton(master=frame, text='disabled', state='disabled', variant=variant).pack()

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    app = bs.App()

    frm = bs.PackFrame(app, padding=16, direction='horizontal').pack()

    bs.Button(app, text="Change Theme", command=bs.toggle_theme).pack(pady=16)

    create_menubutton_frame(frm, "default", 'Solid Menubutton').pack()
    create_menubutton_frame(frm, 'outline', 'Outline Menubutton').pack()
    create_menubutton_frame(frm, 'ghost', 'Ghost Menubutton').pack()

    app.mainloop()
