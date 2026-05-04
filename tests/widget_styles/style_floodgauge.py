import bootstack as bs
from bootstack.constants import *

root = bs.Window("FloodGauge Demo")
style = bs.Style()


p1 = bs.FloodGauge(
    accent="danger",
    mask="Memory Used {}%",
    value=45
)
p1.pack(fill=BOTH, expand=YES, padx=10, pady=10)
p1.start()

btn = bs.Button(text="Change Theme", accent="danger", command=bs.toggle_theme)
btn.pack(padx=10, pady=10)

root.mainloop()
