import bootstack as bs


DARK = 'superhero'
LIGHT = 'flatly'




if __name__ == '__main__':
    # create visual widget style tests
    window = bs.App(theme='darkly')

    bs.Button(text="Change Theme", command=bs.toggle_theme).pack(padx=10, pady=10)
    text = bs.Text(window, font='helvetica 24 bold')
    text.pack(padx=10, pady=10)
    text.insert('end', 'Hello, this is my text.')
    window.mainloop()