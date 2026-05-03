import tkinter as tk
import bootstack as bs

"""
    Test that the `Widget.configure` method is able to change the widget
    style via the `bootstyle` parameter.
"""

root = tk.Tk()
style = bs.Style()
colors = style.theme.colors

btn = bs.Button(root, text="Push Button", bootstyle='outline-danger')
btn.pack(padx=10, pady=10)

ttkstyle = btn.configure('style')
assert ttkstyle == 'danger.Outline.TButton'

