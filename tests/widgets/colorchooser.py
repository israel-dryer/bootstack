import bootstack as bs
from bootstack.dialogs import ColorChooserDialog

app = bs.App(theme="dark", settings=bs.AppSettings(locale="ja"))

cd = ColorChooserDialog(app, initial_color='#adadad')
cd.on_dialog_result(print)

bs.Button(app, text="Show Dialog", command=cd.show).pack()
app.mainloop()
