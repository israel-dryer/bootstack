import bootstack as bs


def hero():
    with bs.App(title="Tabs", minsize=(720, 1), padding=8) as app:
        tabs = bs.Tabs(fill="x")
        with tabs.add("home", label="Home", padding=16, gap=8):
            bs.Label("Home", font="heading-md")
            bs.Label("Welcome to the Home tab.")
        with tabs.add("files", label="Files", padding=16, gap=8):
            bs.Label("Files", font="heading-md")
            bs.Label("Manage your files here.")
        with tabs.add("settings", label="Settings", padding=16, gap=8):
            bs.Label("Settings", font="heading-md")
            bs.Label("Adjust your preferences.")
    app.run()


def icons():
    with bs.App(title="Tabs — Icons", minsize=(720, 1), padding=8) as app:
        tabs = bs.Tabs(fill="x")
        with tabs.add("home",     label="Home",     icon="house",  padding=16, gap=8):
            bs.Label("Home", font="heading-md")
            bs.Label("Welcome to the Home tab.")
        with tabs.add("files",    label="Files",    icon="folder", padding=16, gap=8):
            bs.Label("Files", font="heading-md")
            bs.Label("Manage your files here.")
        with tabs.add("settings", label="Settings", icon="gear",   padding=16, gap=8):
            bs.Label("Settings", font="heading-md")
            bs.Label("Adjust your preferences.")
    app.run()


def vertical():
    with bs.App(title="Tabs — Vertical", size=(520, 280), padding=16) as app:
        tabs = bs.Tabs(orient="vertical", fill="both", expand=True)
        with tabs.add("editor",  label="Editor",  icon="code-slash", padding=16, gap=8):
            bs.Label("Editor", font="heading-md")
            bs.Label("Write your code here.")
        with tabs.add("preview", label="Preview", icon="eye",         padding=16, gap=8):
            bs.Label("Preview", font="heading-md")
            bs.Label("Live preview of your output.")
        with tabs.add("console", label="Console", icon="terminal",    padding=16, gap=8):
            bs.Label("Console", font="heading-md")
            bs.Label("Program output appears here.")
    app.run()


def closable():
    with bs.App(title="Tabs — Closable", minsize=(720, 1), padding=8) as app:
        tabs = bs.Tabs(allow_close=True, fill="x")
        with tabs.add("report", label="Report.pdf",  padding=16, gap=8):
            bs.Label("Report.pdf", font="heading-md")
            bs.Label("Annual report content.")
        with tabs.add("notes",  label="Notes.txt",   padding=16, gap=8):
            bs.Label("Notes.txt", font="heading-md")
            bs.Label("Your notes.")
        with tabs.add("draft",  label="Draft.md",    padding=16, gap=8):
            bs.Label("Draft.md", font="heading-md")
            bs.Label("Work in progress.")
    app.run()


SCENES = {
    "hero":     hero,
    "icons":    icons,
    "vertical": vertical,
    "closable": closable,
}

if __name__ == '__main__':
    vertical()