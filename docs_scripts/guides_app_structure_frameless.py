import bootstack as bs

shell = bs.AppShell(
    title="Custom Window",
    minsize=(1000, 650),
    undecorated=True,
)

shell.mainloop()