import bootstack as bs

with bs.App(title="Checkbox", padding=20, gap=14) as app:

    bs.Label("Basic", font="heading-sm[bold]")
    with bs.HStack(gap=24):
        bs.Checkbox("Unchecked", value=False)
        bs.Checkbox("Checked",   value=True)

    bs.Label("Accent Colors", font="heading-sm[bold]")
    with bs.HStack(gap=16):
        for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
            bs.Checkbox(accent.title(), accent=accent, value=True)

    bs.Label("Tristate", font="heading-sm[bold]")
    with bs.HStack(gap=24):
        bs.Checkbox("Indeterminate", tristate=True)
        bs.Checkbox("Checked",       tristate=True, value=True)
        bs.Checkbox("Unchecked",     tristate=True, value=False)

    bs.Label("Custom State Icons", font="heading-sm[bold]")
    with bs.HStack(gap=24):
        bs.Checkbox("Checked",
            on_icon="check-circle-fill", off_icon="circle",
            show_indicator=False, accent="success", value=True)
        bs.Checkbox("Unchecked",
            on_icon="check-circle-fill", off_icon="circle",
            show_indicator=False, accent="success", value=False)

    bs.Label("Disabled", font="heading-sm[bold]")
    with bs.HStack(gap=24):
        bs.Checkbox("Disabled",         disabled=True)
        bs.Checkbox("Disabled checked", value=True, disabled=True)

app.run()
