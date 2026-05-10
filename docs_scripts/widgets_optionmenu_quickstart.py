import bootstack as bs

app = bs.App()

menu = bs.OptionMenu(
    app,
    value="Medium",
    options=["Low", "Medium", "High"],
)
menu.pack(padx=20, pady=20, fill='x')

app.mainloop()