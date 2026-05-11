import bootstack as bs

app = bs.App()

lv = bs.ListView(
    app,
    items=[{"id": i, "text": f"Item {i}"} for i in range(2000)],
    enable_removing=True,
    enable_dragging=True,
)

def on_sel(_):
    print("selected:", lv.get_selected())

lv.on_selection_changed(on_sel)
lv.pack(fill="both", expand=True, padx=20, pady=20)

app.mainloop()