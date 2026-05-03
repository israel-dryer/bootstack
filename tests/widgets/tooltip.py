import bootstack as bs
from bootstack.constants import *

app = bs.App(size=(400, 100))

b1 = bs.Button(app, text="default tooltip")
b1.pack(side=LEFT, padx=10, pady=10, fill=X, expand=YES)
bs.ToolTip(
    b1,
    text="This is the default tooltip. This elevated background and matching foreground will be applied by default.",
)

b2 = bs.Button(app, text="styled tooltip")
b2.pack(side=LEFT, padx=10, pady=10, fill=X, expand=YES)
bs.ToolTip(
    b2,
    anchor_point="ne",
    window_point="nw",
    text="This is a styled tooltip with less padding. You can change this style by using the `accent` parameter with label style keywords.",
    accent="danger",
)

app.mainloop()
