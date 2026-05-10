from datetime import date
import bootstack as bs

app = bs.App()

cal = bs.Calendar(app, value=date.today(), selection_mode="range", accent="primary")
cal.pack(padx=12, pady=12)

def on_select(e):
    # e.data = {'date': date, 'range': (start, end|None)}
    print(e.data)

cal.on_date_selected(on_select)

app.mainloop()