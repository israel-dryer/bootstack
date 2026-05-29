"""Visual test for public DateField and PathField widgets."""
from datetime import date

import bootstack as bs
from bootstack.widgets import App, VStack, HStack, Label, Separator, DateField, PathField


def main():
    with App(title="DateField + PathField", minsize=(520, 560), padding=20, gap=16) as app:

        Label("DateField", font="heading-lg")

        with HStack(gap=12, fill="x"):
            with VStack(gap=8, fill="x", expand=True):
                Label("Single date (default)")
                df_single = DateField(label="Start date", density="default")

            with VStack(gap=8, fill="x", expand=True):
                Label("With initial value")
                df_value = DateField(
                    value=date.today(),
                    label="Today",
                    message="Pre-filled with today's date",
                )

        with HStack(gap=12, fill="x"):
            with VStack(gap=8, fill="x", expand=True):
                Label("Range mode")
                df_range = DateField(
                    selection_mode="range",
                    label="Date range",
                    message="Pick a start and end date",
                )

            with VStack(gap=8, fill="x", expand=True):
                Label("Disabled")
                df_disabled = DateField(
                    value=date(2025, 1, 1),
                    label="Locked date",
                    disabled=True,
                )

        status_lbl = Label("(pick a date to see value)")

        def on_date_change(e):
            status_lbl.value = f"single value: {df_single.value}"

        df_single.on_change(on_date_change)

        Separator(fill="x")

        Label("PathField", font="heading-lg")

        with HStack(gap=12, fill="x"):
            with VStack(gap=8, fill="x", expand=True):
                Label("Open file (default)")
                pf_open = PathField(label="Select file")

            with VStack(gap=8, fill="x", expand=True):
                Label("Select directory")
                pf_dir = PathField(
                    dialog="directory",
                    label="Directory",
                    message="Pick a folder",
                )

        with HStack(gap=12, fill="x"):
            with VStack(gap=8, fill="x", expand=True):
                Label("Save as")
                pf_save = PathField(
                    dialog="saveasfilename",
                    label="Output file",
                    dialog_options={"defaultextension": ".txt"},
                )

            with VStack(gap=8, fill="x", expand=True):
                Label("Read-only")
                pf_readonly = PathField(
                    value="/some/preset/path.txt",
                    label="Fixed path",
                    read_only=True,
                )

        path_lbl = Label("(browse to see path value)")

        def on_path_change(e):
            path_lbl.value = f"path: {pf_open.value}"

        pf_open.on_change(on_path_change)

    app.run()


if __name__ == "__main__":
    main()