"""Visual test for public DateField and PathField widgets."""
from datetime import date

from bootstack import App, VStack, HStack, Label, Separator, DateField, PathField


with App(title="DateField + PathField", minsize=(1, 560), padding=20, gap=16) as app:

    Label("DateField", font="heading-lg")

    with HStack(gap=12, fill="x", fill_items="x"):
        with VStack(gap=8):
            Label("Single date (default)")
            df_single = DateField(label="Start date", density="default", message=" ")

        with VStack(gap=8, fill="x"):
            Label("With initial value")
            DateField(value=date.today(), label="Today", message="Pre-filled with today's date")

    with HStack(gap=12, fill="x", fill_items="x"):
        with VStack(gap=8):
            Label("Range mode")
            DateField(selection_mode="range", label="Date range", message="Pick a start and end date")

        with VStack(gap=8):
            Label("Disabled")
            DateField(value=date(2025, 1, 1), label="Locked date", disabled=True, message=" ")

    status_lbl = Label("(pick a date to see value)")

    def on_date_change(e):
        status_lbl.value = f"single value: {df_single.value}"

    df_single.on_change(on_date_change)

    Separator(fill="x")

    Label("PathField", font="heading-lg")

    with HStack(gap=12, fill="x", fill_items="x"):
        with VStack(gap=8):
            Label("Open file (default)")
            pf_open = PathField(label="Select file", message=" ")

        with VStack(gap=8):
            Label("Select directory")
            PathField(mode="directory", label="Directory", message="Pick a folder")

    with HStack(gap=12, fill="x", fill_items="x"):
        with VStack(gap=8):
            Label("Save as")
            PathField(mode="save", label="Output file", default_extension=".txt", message=" ")

        with VStack(gap=8, fill="x", fill_items="x"):
            Label("Read-only")
            PathField(value="/some/preset/path.txt", label="Fixed path", read_only=True, message=" ")

    path_lbl = Label("(browse to see path value)")

    def on_path_change(e):
        path_lbl.value = f"path: {pf_open.value}"

    pf_open.on_change(on_path_change)


if __name__ == "__main__":
    app.run()