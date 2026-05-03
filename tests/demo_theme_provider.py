import tkinter as tk

from bootstack.style.theme_provider import ThemeProvider

tk.Tk()

tp = ThemeProvider.instance()
tp.use('dark')

print('theme', tp)
print('typography', tp.typography)
