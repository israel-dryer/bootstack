import tkinter as tk
import bootstack as bs
from random import choice

"""
    Expected Results
    - background is dark
    - only one instance of `BootStyle` or `Tk`
"""

style = bs.Style(theme="darkly")

root = style.master

root.mainloop()