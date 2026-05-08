import bootstack as bs

app = bs.App()

qty = bs.SpinnerEntry(
    app,
    label="Quantity",
    value=1,
    minvalue=0,
    maxvalue=10,
    increment=1,
    message="Select a quantity",
)
qty.pack(fill="x", padx=20, pady=10)

app.mainloop()