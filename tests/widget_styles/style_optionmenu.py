import bootstack as bs

if __name__ == '__main__':
    # create visual widget style tests
    root = bs.App()

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)
    var = bs.Variable()
    om = bs.OptionMenu(root, var, ['dark', 'light'])
    om.pack(padx=10, pady=10, fill='x')

    for i, color in enumerate(['primary', 'secondary', 'success', 'info', 'warning', 'danger']):
        var = bs.Variable()
        om = bs.OptionMenu(root, var, ['primary', 'secondary', 'success', 'info', 'warning', 'danger'], accent=color)
        om.pack(padx=10, pady=10, fill='x')

    root.mainloop()


