import bootstack as bs

app = bs.App()

bs.Button(app, text="Settings", icon="gear").pack(padx=16, pady=16)

app.mainloop()