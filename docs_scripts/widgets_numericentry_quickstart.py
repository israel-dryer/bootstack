import bootstack as bs

app = bs.App()

qty = bs.NumericEntry(
    app,
    label="Quantity",
    value=1,
    minvalue=0,
    maxvalue=999,
    increment=1,
    message="How many items?",
)
qty.pack(fill="x", padx=20, pady=10)

app.mainloop()