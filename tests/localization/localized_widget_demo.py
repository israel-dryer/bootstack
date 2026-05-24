import bootstack as bs

app = bs.App(
    title="Localization Demo",
    settings=bs.AppSettings(locale="ja")
)

var = bs.DoubleVar(value=100)

sl = bs.Scale(app, variable=var, from_=0, to=1000000)
sl.pack(fill='x')

# Label uses a shared variable
bs.Label(app, textvariable=var, value_format='thousands').pack(padx=10, pady=10)

# Label uses the scale variable
bs.Label(app, textvariable=sl.variable, value_format='fixedPoint').pack(padx=10, pady=10)

# Label uses the scale signal
bs.Label(app, textvariable=sl.signal, value_format='currency').pack(padx=10, pady=10)

app.mainloop()