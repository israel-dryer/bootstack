"""Measure the Command/Option binding-vs-display mismatch (#405)."""
from bootstack.shortcuts import Shortcut

def show(pattern):
    s = Shortcut(key="k", pattern=pattern, command=lambda: None)
    return s.pattern, s.binding, s.display

print(f"{'pattern':16} {'binding':22} {'display'}")
for p in ("Command+S", "Option+K", "Mod+S", "Alt+K", "Ctrl+S",
          "Shift+Command+P", "Command+Option+I"):
    pat, b, d = show(p)
    agree = ("Control" in b) == ("Ctrl" in d) and ("Alt" in b) == ("Alt" in d)
    print(f"{pat:16} {b:22} {d:12} {'ok' if agree else 'MISMATCH'}")
