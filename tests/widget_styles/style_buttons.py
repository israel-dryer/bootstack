import bootstack as bs

DARK = 'dark'
LIGHT = 'light'


def button_style_frame(bootstyle, widget_name):
    frame = bs.Frame(root, padding=5)

    title = bs.Label(
        master=frame,
        text=widget_name,
        anchor='center'
    )
    title.pack(padx=5, pady=2, fill='both')

    bs.Separator(frame).pack(padx=5, pady=5, fill='x')

    b = bs.Button(
        master=frame,
        text='Default',
        variant=bootstyle,
        compound="left",
        icon="bootstrap",
    ).pack(padx=5, pady=5, fill='both')

    for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'dark', 'light']:
        bs.Button(
            master=frame,
            text=color.title(),
            accent=color,
            variant=bootstyle,
            compound="left",
            cursor="hand2" if bootstyle == "link" else None,
            icon="bootstrap",
        ).pack(padx=5, pady=5, fill='both')

    bs.Button(
        master=frame,
        text='disabled',
        state='disabled',
        cursor="hand2" if bootstyle == "link" else None,
        accent=color,
        variant=bootstyle,
    ).pack(padx=5, pady=5, fill='both')

    return frame


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.App(theme="ocean-dark")

    button_style_frame('solid', 'Solid Button').pack(side='left')
    button_style_frame('outline', 'Outline Button').pack(side='left')
    button_style_frame('ghost', 'Ghost Button').pack(side='left')
    button_style_frame('text', 'Text Button').pack(side='left')
    button_style_frame('link', 'Link Button').pack(side='left')

    theme_btn = bs.Button(
        root, cursor="hand2", icon="sun", command=lambda: bs.set_theme('light'),
        style_options={"icon_only": True}).pack(padx=10, pady=10)

    bs.Button(
        root, cursor="hand2", icon="moon", command=lambda: bs.set_theme('dark'),
        style_options={"icon_only": True}).pack(padx=10, pady=10)
    root.mainloop()
