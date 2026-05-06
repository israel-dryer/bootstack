"""Demo of the FilterDialog widget.

Shows how to use FilterDialog with and without the undecorated option.
"""
import bootstack as bs
from bootstack.dialogs import FilterDialog


app = bs.Window(theme="dark", size=(500, 500))

# Test button to show the filter dialog with window chrome
def show_filter():
    dialog = FilterDialog(
        master=app,
        title="Select Colors",
        items=[
            "Red",
            "Green",
            {"text": "Blue", "selected": True},
            "Orange",
            "Purple",
            "Yellow",
            "Pink",
            "Brown",
            "Black",
            "White"
        ],
        enable_search=True,
        enable_select_all=True
    )
    result = dialog.show()
    print(f"Selected items: {result}")
    if result:
        result_label.config(text=f"Selected: {', '.join(map(str, result))}")


# Test button to show the filter dialog undecorated
def show_filter_undecorated():
    dialog = FilterDialog(
        master=app,
        title="Select Colors",
        items=[
            "Red",
            "Green",
            {"text": "Blue", "selected": True},
            "Orange",
            "Purple",
            "Yellow",
            "Pink",
            "Brown",
            "Black",
            "White"
        ],
        enable_search=True,
        enable_select_all=True,
        undecorated=True
    )
    result = dialog.show()
    print(f"Selected items (undecorated): {result}")
    if result:
        result_label.config(text=f"Selected: {', '.join(map(str, result))}")


# UI
bs.Label(app, text="FilterDialog Demo", font=("", 16, "bold")).pack(pady=20)
bs.Button(app, text="Show Filter Dialog", command=show_filter).pack(pady=10)
bs.Button(app, text="Show Filter Dialog (Undecorated)", command=show_filter_undecorated).pack(pady=10)
result_label = bs.Label(app, text="No items selected", accent="secondary")
result_label.pack(pady=10)

app.mainloop()