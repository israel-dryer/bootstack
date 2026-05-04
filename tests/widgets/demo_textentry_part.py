import bootstack as bs
from bootstack.widgets.parts.textentry_part import TextEntryPart

root = bs.Window()

# Currency entry with formatting
entry = TextEntryPart(
    root,
    value=12345678.56,
    value_format='#,##0.00'
)
entry.pack()

entry = TextEntryPart(
    root,
    value=12345678.56,
    value_format='#,##0.00'
)
entry.pack()


def on_changed(event):
    print(f"Value changed: {event.data['value']}")


entry.on_changed(on_changed)
root.mainloop()