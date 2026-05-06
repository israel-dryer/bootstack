import bootstack as bs
from bootstack import Font

app = bs.App()
frm = bs.PackFrame(app, gap=8, padding=16)
frm.pack(fill='both')

# Define fonts
title = Font("heading-xl")
body = Font("body")
code = Font("code")

# Apply to widgets
bs.Label(frm, text="Welcome", font=title).pack()
bs.Label(frm, text="This is body text.", font=body).pack()
bs.Label(frm, text="print('Hello')", font=code).pack()

app.mainloop()