import bootstack as bs

app = bs.App()

def on_save():
    print("Saved!")

bs.Button(app, text="Save", command=on_save).pack(padx=20, pady=20)

app.mainloop()