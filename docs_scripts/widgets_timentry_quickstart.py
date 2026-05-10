import bootstack as bs

app = bs.App()

t = bs.TimeEntry(
    app,
    label="Start time",
    value="08:30",
)
t.pack(fill="x", padx=20, pady=10)

app.mainloop()