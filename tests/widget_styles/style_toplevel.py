import bootstack as bs


if __name__ == '__main__':
    # create visual widget style tests
    root = bs.App()

    bs.Label(root, text="Root").pack(padx=10, pady=10)

    top = bs.Toplevel(root)
    bs.Label(top, text="Toplevel").pack(padx=10, pady=10)

    btn = bs.Button(top, text="Change Theme", command=bs.toggle_theme)
    btn.pack(padx=10, pady=10)

    root.after_idle(top.show)

    root.mainloop()