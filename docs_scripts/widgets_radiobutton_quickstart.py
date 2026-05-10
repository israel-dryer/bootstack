import bootstack as bs

app = bs.App()

choice = bs.Signal("medium")

frame = bs.PackFrame(app, direction="horizontal", gap=16, padding=16).pack()

bs.RadioButton(frame, text="Low",    signal=choice, value="low", icon="grid", show_indicator=False).pack()
bs.RadioButton(frame, text="Medium", signal=choice, value="medium").pack()
bs.RadioButton(frame, text="High",   signal=choice, value="high").pack()

app.mainloop()