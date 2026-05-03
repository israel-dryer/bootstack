"""Demo for the inline Calendar widget."""

from datetime import date

import bootstack as bs
from bootstack.constants import BOTH, W, X
from bootstack import Calendar


def main():
    app = bs.Window(title="Calendar Demo", theme="light")

    picker = Calendar(app, start_date=date.today())#, selection_mode="range")
    picker.pack(fill=BOTH, expand=True)

    picker.on_date_selected(print)

    app.mainloop()


if __name__ == "__main__":
    main()