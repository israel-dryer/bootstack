import bootstack as bs
from bootstack.constants import *

root = bs.App(
    theme="dark",
    settings=bs.AppSettings(locale="ko"),
)

frame = bs.Frame(root, padding=10)
frame.pack(padx=10, pady=10)

inner_frame = bs.Frame(frame, padding=10)
inner_frame.pack(padx=10, pady=10)

de = bs.DateEntry(
    inner_frame, label="Registration Date", show_picker_button=True, value_format="longDate", message="Enter the registration date")

de.pack(fill=X)

root.mainloop()
