import bootstack as bs

app = bs.App()

lv = bs.ListView(
    app,
    items=[{"id": i, "text": f"Item {i}"} for i in range(2000)],
    selection_mode="multi",
    show_selection_controls=True,
)

def on_sel(_):
    print("selected:", lv.get_selected())

lv.on_selection_changed(on_sel)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()