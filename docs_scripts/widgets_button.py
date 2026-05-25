import bootstack as bs



app = bs.App()

# solid buttons
solid = bs.Frame(app, padding=(16, 8))
solid.pack(side='top')

bs.Label(solid, font="label", text='Solid', width=10).pack(side='left')
bs.Button(solid, text='default').pack(side='left', padx=8)
solid_active = bs.Button(solid, text='active', state='active')
solid_active.pack(side='left', padx=8)
solid_active.state(['hover'])

solid_focus = bs.Button(solid, text='focus', state='focus')
solid_focus.pack(side='left', padx=8)
solid_focus.state(['focus'])

bs.Button(solid, text='disabled', state='disabled').pack(side='left', padx=8)

# outline buttons
outline = bs.Frame(app, padding=(16, 8))
outline.pack(side='top')

bs.Label(outline, font="label", text='Outline', width=10).pack(side='left')
bs.Button(outline, text='default', variant="outline").pack(side='left', padx=8)
outline_active = bs.Button(outline, text='active', state='active', variant="outline")
outline_active.pack(side='left', padx=8)
outline_active.state(['hover'])

outline_focus = bs.Button(outline, text='focus', state='focus', variant="outline")
outline_focus.pack(side='left', padx=8)
outline_focus.state(['focus'])

bs.Button(outline, text='disabled', state='disabled', variant="outline").pack(side='left', padx=8)

# ghost buttons
ghost = bs.Frame(app, padding=(16, 8))
ghost.pack(side='top')

bs.Label(ghost, font="label", text='Ghost', width=10).pack(side='left')
bs.Button(ghost, text='default', variant="ghost").pack(side='left', padx=8)
ghost_active = bs.Button(ghost, text='active', state='active', variant="ghost")
ghost_active.pack(side='left', padx=8)
ghost_active.state(['hover'])

ghost_focus = bs.Button(ghost, text='focus', state='focus', variant="ghost")
ghost_focus.pack(side='left', padx=8)
ghost_focus.state(['focus'])

bs.Button(ghost, text='disabled', state='disabled', variant="ghost").pack(side='left', padx=8)

icons = bs.Frame(app, padding=(16, 8))
icons.pack(side='top')

bs.Button(icons, text='Settings', icon='gear').pack(side='left', padx=8)
bs.Button(icons, icon='gear', icon_only=True).pack(side='left', padx=8)

colors = bs.Frame(app, padding=(16, 8))
colors.pack(side='top')
for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']:
    bs.Button(colors, text=color.title(), accent=color).pack(side='left', padx=8)

app.mainloop()